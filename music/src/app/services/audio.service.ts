import {Injectable, signal} from '@angular/core';
import {toObservable} from "@angular/core/rxjs-interop";
import {BehaviorSubject} from "rxjs";

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
  private songSubject = new BehaviorSubject<Song | null>(null);

  setSong(song: Song) {
    this.songSubject.next(song)
  }

  getSong() {
    return this.songSubject.asObservable()
  }

  constructor() {}
}
