import {Component, inject, OnDestroy, OnInit} from '@angular/core';
import {NgForOf} from "@angular/common";
import {PlayerComponent} from "../player/player.component";
import {PlaylistComponent} from "../playlist/playlist.component";
import {SongComponent} from "../song/song.component";
import {ActivatedRoute} from "@angular/router";
import {AudioService} from "../../services/audio.service";
import {filter, Subject, Subscription, switchMap, takeUntil} from "rxjs";
import {MusicService} from "../../services/music.service";

@Component({
  selector: 'app-display',
  standalone: true,
  imports: [
    PlayerComponent,
    PlaylistComponent,
    SongComponent,
    NgForOf,
  ],
  templateUrl: './display.component.html',
  styleUrl: './display.component.scss'
})
export class DisplayComponent implements OnInit, OnDestroy {
  private activatedRoute = inject(ActivatedRoute)
  private musicService = inject(MusicService)
  private activatedRoute$: Subscription | undefined

  ngOnInit(): void {
    this.activatedRoute$ = this.activatedRoute.params.pipe(
      filter(params => params["song_id"] != null),
      switchMap(params => this.musicService.getSong(params["song_id"]))
    ).subscribe(
      song => {
        this.musicService.song.set(song)
      }
    )
  }

  ngOnDestroy(): void {
    this.activatedRoute$?.unsubscribe()
  }
}
