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
}

@Injectable({
  providedIn: 'root'
})
export class MusicService {

  currentSong = signal<Song | null>(null);
  playlist = signal<Song[]>([])

  addSongToPlaylist(song: Song) {
    const songs = this.playlist()
    if (!songs.find(s => s.id === song.id)) {
      this.playlist.set([...songs, song])
    }
  }

  private generateRandomWord(s: string): Song {
    const alphabet = 'abcdefghijklmnopqrstuvwxyz';
    let word = '';
    for (let i = 0; i < 4; i++) {
      const randomIndex = Math.floor(Math.random() * alphabet.length);
      word += alphabet[randomIndex];
    }
    return {
      title: s + word,
      artist: null,
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
    console.log("queue", s, shouldFail)
    if (shouldFail) {
      return throwError(() => new Error("Simulated error")).pipe(delay(100));
    } else {
      return of(songs).pipe(delay(100)); // Return the songs with a delay
    }
  }

  getSong(s: string) {
    const song: Song = {
      title: s,
      artist: null,
      id: s
    }
    return of(song).pipe(delay(100));
  }

  getAudio(s: string) {
    console.log("audio", s)
    const url = "https://filesamples.com/samples/audio/mp3/sample2.mp3";
    return of(url).pipe(delay(1000));
  }

  getSongImage(s: string) {
    const image = "img" + s
    console.log("img", s)
    return of(image).pipe(delay(100));
  }
}
