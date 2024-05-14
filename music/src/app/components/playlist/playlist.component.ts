import {Component, inject, OnDestroy, signal} from '@angular/core';
import {Router, RouterLink} from "@angular/router";
import {MusicService, Song} from "../../services/music.service";
import {toObservable} from "@angular/core/rxjs-interop";
import {combineLatest, EMPTY, filter, mergeMap, retry, Subscription} from "rxjs";
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-playlist',
  standalone: true,
  imports: [
    RouterLink,
    NgForOf,
    NgIf
  ],
  templateUrl: './playlist.component.html',
  styleUrl: './playlist.component.scss'
})
export class PlaylistComponent implements OnDestroy {
  private musicService = inject(MusicService)
  router = inject(Router)

  currentSong = this.musicService.currentSong;
  playlist = this.musicService.playlist;
  seedSong = this.musicService.seedSong
  query = signal(true);
  private musicQueue$: Subscription | undefined
  private currentSong$: Subscription | undefined

  constructor() {

    // check if selected song is in the end of query
    // update state if true
    this.currentSong$ = toObservable(this.currentSong).subscribe(
      song => {
        if (!song) return
        const songs = this.musicService.playlist()
        const index = songs.findIndex(s => s.id === song.id)
        if (index === -1) {
          this.query.set(true)
        }
        if (songs.length - index <= 2) {
          this.query.set(true)
        }
      }
    )

    // check if is in 'query' state
    // and if so then start querying using seed song
    // retries if error from backend
    this.musicQueue$ = combineLatest([
      toObservable(this.query),
      toObservable(this.seedSong)
    ]).pipe(
      filter(([q, s]) => q && !!s),
      mergeMap(([_, s]) => {
        if (s) {
          return this.musicService.getQueue(s.id);
        } else {
          return EMPTY;
        }
      })).pipe(retry({delay: 1000})).subscribe(
      songs => {
        const playlist = this.playlist()
        this.playlist.set([...playlist, ...songs])
        this.query.set(false)
      }
    )
  }

  ngOnDestroy(): void {
    this.musicQueue$?.unsubscribe()
    this.currentSong$?.unsubscribe()
  }

  clickOnSong(song: Song) {
    this.currentSong.set(song)
  }

  go() {
    this.router.navigate(["song", "erik1"])
  }

  go2() {
    this.router.navigate(["song", "erik2"])
  }


}
