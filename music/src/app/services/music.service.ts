import {inject, Injectable, signal} from '@angular/core';
import {of, retry} from "rxjs";
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

export interface SongWrapper {
  song: Song
  liked: boolean,
  listened: boolean
}


@Injectable({
  providedIn: 'root'
})
export class MusicService {
  private url = "api/music"
  private delay = 3000
  http = inject(HttpClient)
  currentSong = signal<Song | null>(null);
  playlist = signal<Song[]>([]);
  listenTime = signal(0);

  addSongToPlaylist(song: Song) {
    const songs = this.playlist()
    if (!songs.find(s => s.id === song.id)) {
      this.playlist.set([...songs, song])
    }
  }

  getQueue(s: string) {
    return this.http.get<Song[]>(this.url + "/queue/" + s).pipe(retry({delay: this.delay}))
  }

  getSong(sid: string) {
    // check playlist for song data
    const songs = this.playlist()
    const song = songs.find(s => s.id === sid)
    if (song) return of(song)
    return this.http.get<Song>(this.url + "/song/" + sid)
  }

  postSong(sid: string, time: number) {
    const body = {
      duration: time,
      type: 'listened'
    }
    return this.http.post(this.url + "/song/" + sid, body)
  }

  getAudio(s: string) {
    return this.http.get<string>(this.url + "/song/" + s + "/audio")
  }

  getSongImage(s: string) {
    return this.http.get(this.url + "/song/" + s + "/image", {responseType: 'blob'})
  }
}
