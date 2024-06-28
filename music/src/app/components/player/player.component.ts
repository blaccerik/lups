import {Component, inject, OnDestroy, signal} from '@angular/core';
import {MatToolbar} from "@angular/material/toolbar";
import {MatSlider, MatSliderThumb} from "@angular/material/slider";
import {FormsModule} from "@angular/forms";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {NgIf} from "@angular/common";
import {MusicService} from "../../services/music.service";
import {toObservable} from "@angular/core/rxjs-interop";
import {EMPTY, Subscription, switchMap, tap} from "rxjs";
import {AudioService} from "../../services/audio.service";


@Component({
  selector: 'app-player',
  standalone: true,
  imports: [
    MatToolbar,
    MatSlider,
    FormsModule,
    MatSliderThumb,
    MatIcon,
    MatIconButton,
    NgIf
  ],
  templateUrl: './player.component.html',
  styleUrl: './player.component.scss'
})
export class PlayerComponent implements OnDestroy {
  private musicService = inject(MusicService)
  audioService = inject(AudioService)
  song = this.musicService.currentSong.asReadonly()
  isShowing = signal(false);
  volume = 0.5

  duration = signal(0);
  currentTime = 0;

  private songSrc$: Subscription | undefined

  constructor() {
    this.audioService.audio.ondurationchange = () => {
      this.duration.set(Math.floor(this.audioService.audio.duration));
    }

    this.audioService.audio.ontimeupdate = () => {
      this.currentTime = Math.floor(this.audioService.audio.currentTime);
    }

    this.songSrc$ = toObservable(this.song).pipe(
      // reset states
      tap(() => {
        this.audioService.setSource("", this.volume)
        this.duration.set(0)
        this.currentTime = 0;
      }),
      // query audio
      switchMap(s => s ? this.musicService.getAudio(s.id) : EMPTY)
    ).subscribe(url => {
        this.audioService.setSource(url, this.volume)
        this.audioService.play()
      }
    )
  }

  ngOnDestroy(): void {
    this.songSrc$?.unsubscribe()
    this.audioService.cleanUp()
  }


  toggleMute() {
    if (this.audioService.audio.volume === 0) {
      this.audioService.audio.volume = this.volume
    } else {
      this.audioService.audio.volume = 0
    }
  }

  formatTime(value: number): string {
    const minutes: number = Math.floor(value / 60);
    const seconds: number = value % 60;
    const formattedMinutes: string = minutes < 10 ? '0' + minutes : '' + minutes;
    const formattedSeconds: string = seconds < 10 ? '0' + seconds : '' + seconds;
    return `${formattedMinutes}:${formattedSeconds}`;
  }

  onTimeChange(value: number) {
    this.audioService.audio.currentTime = value
  }

  onVolumeChange(value: number) {
    this.audioService.audio.volume = value
    this.volume = value
  }
}
