import {Component, inject, OnDestroy, signal} from '@angular/core';
import {Router, RouterLink} from "@angular/router";
import {MusicService, Song} from "../../services/music.service";
import {toObservable} from "@angular/core/rxjs-interop";
import {combineLatest, EMPTY, filter, mergeMap, retry, Subscription} from "rxjs";
import {NgForOf, NgIf} from "@angular/common";

@Component({
  selector: 'app-playlist',
  standalone: true,
  imports: [
    RouterLink,
    NgForOf,
    NgIf
  ],
  templateUrl: './playlist.component.html',
  styleUrl: './playlist.component.scss'
})
export class PlaylistComponent {
  private musicService = inject(MusicService)
  router = inject(Router)

  currentSong = this.musicService.currentSong;
  playlist = this.musicService.playlist;

  clickOnSong(song: Song) {
    this.currentSong.set(song)
  }

  go() {
    this.router.navigate(["song", "erik1"])
  }

  go2() {
    this.router.navigate(["song", "erik2"])
  }


}
