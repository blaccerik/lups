import {Injectable, signal} from '@angular/core';
import {toObservable} from "@angular/core/rxjs-interop";
import {BehaviorSubject, interval, take} from "rxjs";

export interface Artist {
  name: string;
  id: string
}

export interface Song {
  id: string;
  title: string;
  artist: Artist | null;
  src: string
}

@Injectable({
  providedIn: 'root'
})
export class AudioService {
  song = signal<Song | null>(null)
  // private songSubject = new BehaviorSubject<Song | null>(null);
  //
  // setSong(song: Song) {
  //   this.songSubject.next(song)
  // }
  //
  // getSong(a: string) {
  //   console.log(a)
  //   return this.songSubject.asObservable()
  // }
  //
  // constructor() {
  //   // Emit a value every second
  //   interval(1000).subscribe(() => {
  //     this.songSubject.next(null);
  //   });
  // }
}
