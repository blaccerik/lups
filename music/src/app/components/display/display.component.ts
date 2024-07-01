import {Component, inject, OnDestroy, SecurityContext} from '@angular/core';
import {NgForOf} from "@angular/common";
import {PlayerComponent} from "../player/player.component";
import {PlaylistComponent} from "../playlist/playlist.component";
import {SongComponent} from "../song/song.component";
import {ActivatedRoute, Router} from "@angular/router";
import {concatMap, Subscription, switchMap, tap, throttleTime} from "rxjs";
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
  private songs: Subscription | undefined
  currentSong = this.musicService.currentSong;
  playlist = this.musicService.playlist;
  // query = this.musicService.query;


  constructor() {
    // // listen for route changes and update current song
    this.activatedRoute$ = this.activatedRoute.params.pipe(
      tap(() => {
          this.currentSong.set(null);
          this.playlist.set([]);
        }
      ),
      // re query if needed
      switchMap(params =>
        this.musicService.getQuery().pipe(
          throttleTime(1000),
          switchMap(() => this.musicService.getQueue(params["queue_id"]))
        )
      ),
      tap(songs => {
        this.musicService.addSongsToPlaylist(songs)
      }),
      concatMap(songs => songs),
      // filter(song => !song.image),
      concatMap(song => this.musicService.getSongImage(song.id))
    ).subscribe(
      imgBlob => {
        const objectURL = URL.createObjectURL(imgBlob.blob);
        const imageUrl = this.sanitizer.bypassSecurityTrustUrl(objectURL);
        const playlist = this.playlist();
        const song = playlist.find(p => p.id === imgBlob.songId);
        if (!song) return;
        const image = this.sanitizer.sanitize(SecurityContext.URL, imageUrl);
        if (!image) return;
        song.image = image;
        this.playlist.set([...playlist]);
        // current song needs to be updated separately
        const currentSong = this.currentSong();
        if (!currentSong) return;
        if (currentSong.id === song.id) {
          currentSong.image = image;
          this.currentSong.set({...currentSong});
        }
      }
    )
  }


  ngOnDestroy(): void {
    this.activatedRoute$?.unsubscribe()
    this.songs?.unsubscribe()
  }
}
