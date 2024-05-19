import {Component, inject, OnDestroy, signal} from '@angular/core';
import {NgForOf} from "@angular/common";
import {PlayerComponent} from "../player/player.component";
import {PlaylistComponent} from "../playlist/playlist.component";
import {SongComponent} from "../song/song.component";
import {ActivatedRoute} from "@angular/router";
import {combineLatest, EMPTY, filter, mergeMap, retry, Subscription, switchMap} from "rxjs";
import {MusicService, Song} from "../../services/music.service";
import {toObservable} from "@angular/core/rxjs-interop";

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

  currentSong = this.musicService.currentSong;
  playlist = this.musicService.playlist;
  seedSong = signal<null | Song>(null)
  query = signal(true);

  private activatedRoute$: Subscription | undefined
  private currentSong$: Subscription | undefined
  private musicQueue$: Subscription | undefined


  constructor() {
    // listen for route changes and update signals
    this.activatedRoute$ = this.activatedRoute.params.pipe(
      filter(params => params["song_id"] != null),
      switchMap(params => this.musicService.getSong(params["song_id"]))
    ).subscribe(
      song => {
        this.musicService.currentSong.set(song);
        this.musicService.addSongToPlaylist(song);
        if (!this.seedSong()) {
          this.seedSong.set(song)
        }
      }
    )

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
      mergeMap(([q, s]) => q && s ? this.musicService.getQueue(s.id) : EMPTY)
    ).pipe(retry({delay: 1000})).subscribe(
      songs => {
        const playlist = this.playlist()
        this.playlist.set([...playlist, ...songs])
        this.query.set(false)
      }
    )
  }

  ngOnDestroy(): void {
    this.activatedRoute$?.unsubscribe()
    this.currentSong$?.unsubscribe()
    this.musicQueue$?.unsubscribe()
  }
}
