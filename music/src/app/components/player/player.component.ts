import {Component, computed, effect, inject, OnDestroy, OnInit, signal} from '@angular/core';
import {MatToolbar} from "@angular/material/toolbar";
import {MatSlider, MatSliderThumb} from "@angular/material/slider";
import {FormsModule} from "@angular/forms";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {NgIf} from "@angular/common";
import {AudioService} from "../../services/audio.service";
import {Subscription} from "rxjs";
import {toObservable} from "@angular/core/rxjs-interop";
import {MusicService} from "../../services/music.service";


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
export class PlayerComponent implements OnInit, OnDestroy {

  // private audioService = inject(AudioService)
  private musicService = inject(MusicService)
  isShowing = signal(false);
  audio = computed(() => {
    const song = this.musicService.song();
    if (!song) return;
    const audio = new Audio(song.src);
    this.duration = 0
    this.currentTime = 0
    audio.ondurationchange = () => {
      this.duration = Math.floor(audio.duration);
    }
    audio.ontimeupdate = () => {
      this.currentTime = Math.floor(audio.currentTime);
    }
    return audio;
  })
  // they are not know when audio object is created :(
  duration = 0;
  currentTime = 0;
  volume = signal(0.5)
  prevVolume = signal(0.5)

  constructor() {}

  ngOnInit(): void {

  }

  ngOnDestroy() {
  }


  toggleMute() {
    const audio = this.audio()
    if (!audio) return

    if (audio.volume === 0) {
      const vol = this.prevVolume()
      this.volume.set(vol)
      audio.volume = vol
    } else {
      this.volume.set(0)
      audio.volume = 0
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
    const audio = this.audio()
    if (!audio) return
    if (audio.readyState < 2) return;
    if (audio.paused) {
      audio.play();
    } else {
      audio.pause();
    }
  }

  onTimeChange(value: number) {
    const audio = this.audio()
    if (!audio) return
    audio.currentTime = value
  }

  onVolumeChange(value: number) {
    const audio = this.audio()
    if (!audio) return
    audio.volume = value
    this.volume.set(value);
    this.prevVolume.set(value)

  }
}
