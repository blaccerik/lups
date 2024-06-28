import {Component, inject, OnDestroy, SecurityContext} from '@angular/core';
import {NgForOf} from "@angular/common";
import {PlayerComponent} from "../player/player.component";
import {PlaylistComponent} from "../playlist/playlist.component";
import {SongComponent} from "../song/song.component";
import {ActivatedRoute, Router} from "@angular/router";
import {concatMap, filter, Subscription, switchMap, tap} from "rxjs";
import {MusicService} from "../../services/music.service";
import {DomSanitizer} from "@angular/platform-browser";

@Component({
  selector: 'app-display',
  standalone: true,
  imports: [
    PlayerComponent,
    PlaylistComponent,
    SongComponent,
    NgForOf,
  ],
  templateUrl: './display.component.html',
  styleUrl: './display.component.scss'
})
export class DisplayComponent implements OnDestroy {
  private activatedRoute = inject(ActivatedRoute)
  private router = inject(Router)
  private sanitizer = inject(DomSanitizer)
  private musicService = inject(MusicService)
  private activatedRoute$: Subscription | undefined
  currentSong = this.musicService.currentSong;
  playlist = this.musicService.playlist;

  constructor() {

    // listen for route changes and update current song
    this.activatedRoute$ = this.activatedRoute.params.pipe(
      filter(params => params["queue_id"] !== null),

      // reset states
      tap(() => {
          const prevSong = this.currentSong();
          if (prevSong) this.sendData(prevSong.id);
          this.currentSong.set(null);
          this.playlist.set([])
        }
      ),
      // get song for queue
      switchMap(params => this.musicService.getQueue(params["queue_id"])),
      tap(songs => {
        this.playlist.set(songs)
        this.currentSong.set(songs[0])
      }),
      // flatten list
      switchMap(songs => songs),
      // filter only songs which don't have an image
      filter(song => {
        console.log(song.id)
        return true
      }),
      // query images for songs
      concatMap(song => this.musicService.getSongImage(song.id))
    ).subscribe(imgBlob => {
      const objectURL = URL.createObjectURL(imgBlob.blob);
      const imageUrl = this.sanitizer.bypassSecurityTrustUrl(objectURL);
      const playlist = this.playlist()
      const song = playlist.find(p => p.id === imgBlob.songId);
      if (!song) return;
      const image = this.sanitizer.sanitize(SecurityContext.URL, imageUrl);
      if (!image) return;
      song.image = image;
      this.playlist.set([...playlist]);
      // current song needs to be updated separately
      const currentSong = this.currentSong()
      if (!currentSong) return;
      if (currentSong.id === song.id) {
        currentSong.image = image
        this.currentSong.set({...currentSong})
      }
      }
    )
  }

  private sendData(sid: string) {
    // send metadata to backend
    const time = this.musicService.listenTime();
    if (time > 3) this.musicService.postSong(sid, time).subscribe()
    this.musicService.listenTime.set(0)
  }

  ngOnDestroy(): void {
    this.activatedRoute$?.unsubscribe()
  }
}
