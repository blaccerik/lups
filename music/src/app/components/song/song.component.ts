import {Component, computed, inject, OnDestroy, signal} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {MatIconButton} from "@angular/material/button";
import {MatIcon} from "@angular/material/icon";
import {NgForOf, NgIf, NgOptimizedImage} from "@angular/common";
import {MusicService} from "../../services/music.service";
import {YouTubePlayer} from '@angular/youtube-player';
import {Subscription} from "rxjs";
import {DomSanitizer} from "@angular/platform-browser";
import {AudioService} from "../../services/audio.service";
import {animate, state, style, transition, trigger} from "@angular/animations";

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
    NgForOf,
    NgIf,
    NgOptimizedImage
  ],
  templateUrl: './song.component.html',
  styleUrl: './song.component.scss',
  animations: [
    trigger('growShrink', [
      state('void', style({
        scale: 2,
        opacity: 0.75
      })),
      state('*', style({
        scale: 4,
        opacity: 0
      })),
      transition('void => *', [
        animate('0.3s ease-in')
      ]),
    ])
  ]
})
export class SongComponent implements OnDestroy {
  private musicService = inject(MusicService)
  private sanitizer = inject(DomSanitizer)
  audioService = inject(AudioService)
  song = this.musicService.currentSong.asReadonly()
  title = computed(() => {
    return this.song()?.title ?? ":("
  })
  author = computed(() => this.song()?.artist?.name ?? ":(")
  img = computed(() => {
    return this.song()?.image
  })
  private songImg$: Subscription | undefined

  constructor() {
  }

  ngOnDestroy(): void {
    this.songImg$?.unsubscribe()
  }

  click() {
    this.audioService.play()
    this.triggerAnimation()
  }

  showIcon = signal(false)

  triggerAnimation() {
    this.showIcon.set(true)
  }

  onAnimationDone() {
    this.showIcon.set(false)
  }
}
