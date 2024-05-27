import {inject, Injectable, signal} from '@angular/core';
import {catchError, EMPTY, map, Observable, of, retry, throwError} from "rxjs";
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
  count: number,
  song_id: string
}

export interface SingleSong {
  song?: Song
  status: string
}

export interface SongQueue {
  songs: Song[]
  status: string
}


@Injectable({
  providedIn: 'root'
})
export class MusicService {
  private url = "api/music"
  private delay = 2000
  private count = 3
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
    return this.http.get<SongQueue>(this.url + "/queue/" + s).pipe(
      catchError(() => {
        return EMPTY
      }),
      map(sq => {
        if (sq.status == "ready") return sq.songs
        throw new Error("empty")
      }),
      retry({delay: this.delay, count: this.count})
    )
  }

  getSong(sid: string): Observable<Song> {
    // check playlist for song data
    const songs = this.playlist()
    const song = songs.find(s => s.id === sid)
    if (song) return of(song)
    return this.http.get<SingleSong>(this.url + "/song/" + sid).pipe(
      catchError(() => {
        return EMPTY
      }),
      map(ss => {
        if (ss.status == "ready" && ss.song) return ss.song
        throw new Error("empty")
      }),
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
