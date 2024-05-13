import {Component, effect, inject, OnDestroy, OnInit, signal} from '@angular/core';
import {MatToolbar} from "@angular/material/toolbar";
import {MatSlider, MatSliderThumb} from "@angular/material/slider";
import {FormsModule} from "@angular/forms";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {NgIf} from "@angular/common";
import {AudioService} from "../../services/audio.service";
import {Subscription} from "rxjs";


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

  private audioService = inject(AudioService)
  isShowing = signal(false);
  audio = new Audio();
  duration = 0;
  currentTime = 0;
  volume = 0.5;

  url = "https://download.samplelib.com/mp3/sample-9s.mp3"

  constructor() {}

  song$: Subscription | undefined

  ngOnInit(): void {
    this.song$ = this.audioService.getSong().subscribe(
      song => {
        if (!song) return
        this.audio.src = song.src

        // Listen to the progress event to track the download progress
        this.audio.addEventListener('progress', () => {
          // Calculate the percentage of the audio file downloaded
          const bufferedTime = this.audio.buffered.end(0); // Time buffered
          const totalTime = this.audio.duration; // Total time of the audio
          const percentage = (bufferedTime / totalTime) * 100;

          console.log(`Downloaded: ${percentage}%`);
        });

        this.audio.ondurationchange = () => {
          this.duration = Math.floor(this.audio.duration);
        }
        this.audio.ontimeupdate = () => {
          this.currentTime = Math.floor(this.audio.currentTime);
        }
      }
    )
  }

  ngOnDestroy() {
    if (this.song$) this.song$.unsubscribe();
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
    if (this.audio.readyState < 2) return
    if (this.audio.paused) {
      this.audio.play();
    } else {
      this.audio.pause();
    }
  }

  onTimeChange(value: number) {
    this.audio.currentTime = value
  }

  onVolumeChange(value: number) {
    this.volume = value;
  }
}
