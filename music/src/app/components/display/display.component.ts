import {Component, inject, OnDestroy} from '@angular/core';
import {NgForOf} from "@angular/common";
import {PlayerComponent} from "../player/player.component";
import {PlaylistComponent} from "../playlist/playlist.component";
import {SongComponent} from "../song/song.component";
import {ActivatedRoute} from "@angular/router";
import {filter, Subscription, switchMap, tap} from "rxjs";
import {MusicService} from "../../services/music.service";

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
  private musicService = inject(MusicService)
  private activatedRoute$: Subscription | undefined
  currentSong = this.musicService.currentSong;

  constructor() {
    // listen for route changes and update current song
    this.activatedRoute$ = this.activatedRoute.params.pipe(
      filter(params => params["song_id"] !== null),
      tap(() => {
          const prevSong = this.currentSong();
          if (prevSong) this.sendData(prevSong.id);
          this.musicService.currentSong.set(null);
        }
      ),
      switchMap(params => this.musicService.getSong(params["song_id"]))
    ).subscribe(song => {
        this.currentSong.set(song);
        this.musicService.addSongToPlaylist(song);
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
