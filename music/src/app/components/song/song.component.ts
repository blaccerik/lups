import {Component, inject, OnDestroy, signal} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {MatIconButton} from "@angular/material/button";
import {MatIcon} from "@angular/material/icon";
import {NgForOf} from "@angular/common";
import {MusicService} from "../../services/music.service";
import {YouTubePlayer} from '@angular/youtube-player';
import {toObservable} from "@angular/core/rxjs-interop";
import {EMPTY, Subscription, switchMap} from "rxjs";

@Component({
  selector: 'app-song',
  standalone: true,
  imports: [
    YouTubePlayer,
    MatDrawerContainer,
    MatDrawer,
    MatDrawerContent,
    MatIconButton,
    MatIcon,
    NgForOf
  ],
  templateUrl: './song.component.html',
  styleUrl: './song.component.scss'
})
export class SongComponent implements OnDestroy {
  private musicService = inject(MusicService)
  song = this.musicService.currentSong.asReadonly()
  img = signal<string | null>(null)

  private songImg$: Subscription | undefined
  private song$: Subscription | undefined

  constructor() {
    // reset image
    this.song$ = toObservable(this.song).subscribe(
      song => {
        if (!song) return
        this.img.set(null)
      })
    // update song image
    this.songImg$ = toObservable(this.song)
      .pipe(switchMap(s => s ? this.musicService.getSongImage(s.id) : EMPTY))
      .subscribe(img => this.img.set(img))
  }

  ngOnDestroy(): void {
    this.songImg$?.unsubscribe()
    this.song$?.unsubscribe()
  }
}
