import {Component, effect, inject, OnDestroy, signal} from '@angular/core';
import {MatToolbar} from "@angular/material/toolbar";
import {MatSlider, MatSliderThumb} from "@angular/material/slider";
import {FormsModule} from "@angular/forms";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {NgIf} from "@angular/common";
import {MusicService} from "../../services/music.service";
import {toObservable} from "@angular/core/rxjs-interop";
import {EMPTY, Subscription, switchMap} from "rxjs";


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
  song = this.musicService.currentSong.asReadonly()
  isShowing = signal(false);
  volume = 0.5
  audio = new Audio();
  duration = 0;
  currentTime = 0;

  private songSrc$: Subscription | undefined

  constructor() {
    effect(() => {
      const song = this.musicService.currentSong();
      if (!song) return;
      this.audio.src = ""
      this.audio.volume = this.volume
      this.duration = 0
      this.currentTime = 0
      this.audio.ondurationchange = () => {
        this.duration = Math.floor(this.audio.duration);
      }
      this.audio.ontimeupdate = () => {
        this.currentTime = Math.floor(this.audio.currentTime);
      }
    });

    // get song new src
    this.songSrc$ = toObservable(this.song)
      .pipe(switchMap(s => s ? this.musicService.getAudio(s.id) : EMPTY))
      .subscribe(url => this.audio.src = url)
  }

  ngOnDestroy(): void {
    this.songSrc$?.unsubscribe()
  }


  toggleMute() {
    if (this.audio.volume === 0) {
      this.audio.volume = this.volume
    } else {
      this.audio.volume = 0
    }
  }

  formatTime(value: number): string {
    const minutes: number = Math.floor(value / 60);
    const seconds: number = value % 60;
    const formattedMinutes: string = minutes < 10 ? '0' + minutes : '' + minutes;
    const formattedSeconds: string = seconds < 10 ? '0' + seconds : '' + seconds;
    return `${formattedMinutes}:${formattedSeconds}`;
  }

  play(): void {
    if (this.audio.readyState < 2) return;
    if (this.audio.paused) {
      this.audio.play().then();
    } else {
      this.audio.pause();
    }
  }

  onTimeChange(value: number) {
    this.audio.currentTime = value
  }

  onVolumeChange(value: number) {
    this.audio.volume = value
    this.volume = value
  }
}
