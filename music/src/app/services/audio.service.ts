import {inject, Injectable} from '@angular/core';
import {MusicService} from "./music.service";

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  private musicService = inject(MusicService)
  listenTime = this.musicService.listenTime
  audio = new Audio();
  timer: any
  setSource(src: string, volume: number) {
    this.audio.src = src;
    this.audio.volume = volume;
  }

  private startTimer() {
    clearInterval(this.timer)
    this.timer = setInterval(() => {
      this.listenTime.update(v => v + 1)
    }, 1000);
  }


  play(): void {
    if (this.audio.paused) {
      // if user hasn't interacted with site then audio cant play
      try {
        // todo remove
        // this.audio.play().then();
        // this.startTimer()
      } catch {
      }
    } else {
      this.audio.pause();
      clearInterval(this.timer);
    }
  }

  cleanUp() {
    clearInterval(this.timer)
    this.audio.pause()
  }
}
