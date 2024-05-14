import {Injectable, signal} from '@angular/core';
import {BehaviorSubject, delay, of} from "rxjs";
import {Song} from "./audio.service";

@Injectable({
  providedIn: 'root'
})
export class MusicService {

  song = signal<Song | null>(null);

  // replace with backend call
  getSong(s: string) {
    const song: Song = {
      title: s,
      artist: null,
      src: "https://filesamples.com/samples/audio/mp3/sample2.mp3",
      id: s
    }
    return of(song).pipe(delay(100));
  }

  constructor() { }
}
