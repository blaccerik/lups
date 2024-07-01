import {inject, Injectable, signal} from '@angular/core';
import {BehaviorSubject, map, Observable, of, retry} from "rxjs";
import {HttpClient} from "@angular/common/http";

export interface Artist {
  name: string;
  id: string
}


export interface Song {
  id: string;
  title: string;
  artist: Artist | null;
  length: number;
  type: string;
  image?: string
}

export interface QueuePrevious {
  song: Song
  hidden: boolean,
}

export interface ImageBlob {
  blob: Blob,
  songId: string
}


@Injectable({
  providedIn: 'root'
})
export class MusicService {
  private url = "api/music"
  private delay = 1000
  private count = 5
  private http = inject(HttpClient)
  currentSong = signal<Song | null>(null);
  playlist = signal<Song[]>([]);
  listenTime = signal(0);
  private query = new BehaviorSubject<void>(undefined);


  addSongsToPlaylist(songs: Song[]) {
    const playListSongs = this.playlist()
    for (const song of songs) {
      if (!playListSongs.find(s => s.id === song.id)) {
        playListSongs.push(song)
      }
    }
    this.playlist.set([...playListSongs])
    if (!this.currentSong()) {
      this.currentSong.set(songs[0])
    }
  }

  private postData(sid: string) {
    // send metadata to backend
    const time = this.listenTime();
    if (time > 3) this.postSong(sid, time).subscribe()
    this.listenTime.set(0)
  }

  setCurrentSong(song: Song) {
    const old = this.currentSong()
    if (old) this.postData(old.id)
    this.currentSong.set(song)
  }

  reQuerySongs() {
    this.query.next()
  }

  getQuery() {
    return this.query.asObservable()
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

  getSongImage(s: string): Observable<ImageBlob> {
    return this.http.get(this.url + "/song/" + s + "/image", {responseType: 'blob'}).pipe(
      map(b => {
        return {blob: b, songId: s}
      }))
  }

  getQueuePrev() {
    return this.http.get<QueuePrevious[]>(`${this.url}/queue/previous`)
  }


  getQueue(s: string): Observable<Song[]> {
    return this.http.get<Song[]>(this.url + "/queue/" + s).pipe(
      retry({delay: this.delay, count: this.count})
    )
  }

  getNewSongs() {
    return this.http.get<Song[]>(this.url + "/queue/new")
  }
}
