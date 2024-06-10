import {inject, Injectable, signal} from '@angular/core';
import {Observable, of, retry} from "rxjs";
import {HttpClient} from "@angular/common/http";

export interface Artist {
  name: string;
  id: string
}

export interface Song {
  id: string;
  title: string;
  artist: Artist | null;
}

export interface PreviousSongQueue {
  song_id: string,
  song_nr: number,
  hidden: boolean,
  image?: boolean
}


@Injectable({
  providedIn: 'root'
})
export class MusicService {
  private url = "api/music"
  private delay = 1000
  private count = 5
  http = inject(HttpClient)
  currentSong = signal<Song | null>(null);
  playlist = signal<Song[]>([]);
  listenTime = signal(0);

  addSongsToPlaylist(songs: Song[]) {
    const playListSongs = this.playlist()
    for (const song of songs) {
      if (!playListSongs.find(s => s.id === song.id)) {
        playListSongs.push(song)
      }
    }
    this.playlist.set([...playListSongs])
  }

  getQueue(s: string): Observable<Song[]> {
    return this.http.get<Song[]>(this.url + "/queue/" + s).pipe(
      retry({delay: this.delay, count: this.count})
    )
  }

  getSong(sid: string): Observable<Song> {
    // check playlist for song data
    const songs = this.playlist()
    const song = songs.find(s => s.id === sid)
    if (song) return of(song)
    return this.http.get<Song>(this.url + "/song/" + sid).pipe(
      retry({delay: this.delay, count: this.count})
    )
  }

  postSong(sid: string, time: number) {
    const body = {
      duration: time,
      liked: false
    }
    return this.http.post(this.url + "/song/" + sid, body)
  }

  getAudio(s: string) {
    return this.http.get<string>(this.url + "/song/" + s + "/audio")
  }

  getSongImage(s: string) {
    return this.http.get(this.url + "/song/" + s + "/image", {responseType: 'blob'})
  }

  getQueuePrev() {
    return this.http.get<PreviousSongQueue[]>(this.url + "/queue/previous")
  }
}
