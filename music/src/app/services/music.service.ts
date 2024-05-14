import {Injectable, signal} from '@angular/core';
import {delay, of, throwError} from "rxjs";

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
export class MusicService {

  currentSong = signal<Song | null>(null);
  seedSong = signal<Song | null>(null);
  playlist = signal<Song[]>([])

  addSongToPlaylist(song: Song) {
    const songs = this.playlist()
    if (!songs.find(s => s.id === song.id)) {
      this.playlist.set([...songs, song])
    }
  }

  setSeedSong(song: Song) {
    if (!this.seedSong()) {
      this.seedSong.set(song)
    }
  }

  generateRandomWord(s: string): Song {
    const alphabet = 'abcdefghijklmnopqrstuvwxyz';
    let word = '';
    for (let i = 0; i < 4; i++) {
      const randomIndex = Math.floor(Math.random() * alphabet.length);
      word += alphabet[randomIndex];
    }
    return {
      title: s + word,
      artist: null,
      src: "https://filesamples.com/samples/audio/mp3/sample2.mp3",
      id: word
    }
  }


  getQueue(s: string) {
    const songs: Song[] = [
      this.generateRandomWord(s),
      this.generateRandomWord(s),
      this.generateRandomWord(s),
      this.generateRandomWord(s)
    ]
    const shouldFail = Math.random() > 0.5;
    console.log("shouldfail", s, shouldFail)
    if (shouldFail) {
      return throwError(() => new Error("Simulated error"));
    } else {
      return of(songs); // Return the songs with a delay
    }
  }

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
}
