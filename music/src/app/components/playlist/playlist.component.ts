import {Component, inject, OnDestroy, signal} from '@angular/core';
import {Router, RouterLink} from "@angular/router";
import {MusicService, Song} from "../../services/music.service";
import {Subscription} from "rxjs";
import {NgForOf, NgIf, NgOptimizedImage, NgStyle} from "@angular/common";
import {scheduleObservable} from "rxjs/internal/scheduled/scheduleObservable";

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

  currentSong = this.musicService.currentSong;
  playlist = this.musicService.playlist;
  query = signal(true);

  private currentSong$: Subscription | undefined
  private musicQueue$: Subscription | undefined
  private playlist$: Subscription | undefined

  constructor() {

    // // check if selected song is in the end of query
    // // update state if true
    // this.currentSong$ = toObservable(this.currentSong).subscribe(
    //   song => {
    //     if (!song) return
    //     if (this.seedSong() === null) {
    //       this.seedSong.set(song);
    //     }
    //     const songs = this.playlist()
    //     const index = songs.findIndex(s => s.id === song.id)
    //     if (index === -1) {
    //       this.query.set(true)
    //     }
    //     if (songs.length - index <= 2) {
    //       this.query.set(true)
    //     }
    //   }
    // )
    // // check if is in 'query' state
    // // and if so then start querying using seed song
    // // retries if error from backend
    // this.musicQueue$ = combineLatest([
    //   toObservable(this.query),
    //   toObservable(this.seedSong)
    // ]).pipe(
    //   filter(([q, s]) => q && !!s),
    //   mergeMap(([q, s]) => q && s ? this.musicService.getQueue(s.id) : EMPTY)
    // ).subscribe(
    //   songs => {
    //     this.musicService.addSongsToPlaylist(songs)
    //     this.query.set(false)
    //   }
    // )
    // this.playlist$ = toObservable(this.playlist).pipe(
    //   switchMap(data => data), // flatten the array of items into individual items
    //   filter(song => !song.image),
    //   mergeMap(song => this.musicService.getSongImage(song.id))
    // ).subscribe(imageBlob=> {
    //   const playlist = this.playlist()
    //   const song = playlist.find(p => p.id === imageBlob.songId)
    //   if (!song) return;
    //   song.image = URL.createObjectURL(imageBlob.blob)
    //   // this.playlist.set([...playlist])
    //   }
    // )
  }

  clickOnSong(song: Song) {
    this.currentSong.set(song)
  }


  ngOnDestroy(): void {
    this.currentSong$?.unsubscribe()
    this.musicQueue$?.unsubscribe()
    this.playlist$?.unsubscribe()
  }

  protected readonly scheduleObservable = scheduleObservable;
  protected readonly Number = Number;
}
