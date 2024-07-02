import {Component, inject, OnDestroy, signal} from '@angular/core';
import {Router, RouterLink} from "@angular/router";
import {MusicService, Song} from "../../services/music.service";
import {Subscription} from "rxjs";
import {NgForOf, NgIf, NgOptimizedImage, NgStyle} from "@angular/common";
import {scheduleObservable} from "rxjs/internal/scheduled/scheduleObservable";
import {toObservable} from "@angular/core/rxjs-interop";

@Component({
  selector: 'app-playlist',
  standalone: true,
  imports: [
    RouterLink,
    NgForOf,
    NgIf,
    NgOptimizedImage,
    NgStyle
  ],
  templateUrl: './playlist.component.html',
  styleUrl: './playlist.component.scss'
})
export class PlaylistComponent implements OnDestroy {
  private musicService = inject(MusicService)
  router = inject(Router)

  currentSong = this.musicService.currentSong.asReadonly();
  playlist = this.musicService.playlist.asReadonly();
  // todo maybe if more songs are added scrollbar might stop working
  // not sure tho?

  private currentSong$: Subscription | undefined

  constructor() {

    // check if selected song is in the end of query
    // update state if true
    this.currentSong$ = toObservable(this.currentSong).subscribe(
      song => {
        if (!song) return
        const songs = this.playlist()
        const index = songs.findIndex(s => s.id === song.id)
        if (index === -1) return;
        if (songs.length - index <= 3) {
          this.musicService.reQuerySongs()
        }
      }
    )
  }

  clickOnSong(song: Song) {
    this.musicService.setCurrentSong(song)
  }


  ngOnDestroy(): void {
    this.currentSong$?.unsubscribe()
  }
}
