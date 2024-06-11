import {Component, computed, inject, OnDestroy, signal} from '@angular/core';
import {MusicService, PreviousSongQueue} from "../../services/music.service";
import {mergeMap, Subscription, switchMap, tap} from "rxjs";
import {Router} from "@angular/router";
import {NgClass, NgForOf, NgIf, NgOptimizedImage} from "@angular/common";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {MatSuffix} from "@angular/material/form-field";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    NgForOf,
    NgOptimizedImage,
    NgClass,
    MatIcon,
    MatIconButton,
    MatSuffix,
    MatMiniFabButton,
    NgIf
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnDestroy {
  musicService = inject(MusicService)
  router = inject(Router)
  queuePrev$: Subscription | undefined
  queuePrev = signal<null | PreviousSongQueue[]>(null)
  sortedQueue = computed(() => {
    const queue = this.queuePrev()
    if (!queue) return []
    const h = this.hidden()
    const asc = this.asc()
    return queue
      .filter(q => q.hidden === h)
      .sort((a, b) => a.song_nr - (b.song_nr * asc))
  })
  asc = signal(-1)
  hidden = signal(false)

  constructor() {
    this.queuePrev$ = this.musicService.getQueuePrev().pipe(
      tap(data => this.queuePrev.set(data)),
      switchMap(data => data), // flatten the array of items into individual items
      mergeMap(item => this.musicService.getSongImage(item.song_id)) // process each item as soon as it's emitted
    ).subscribe(imageBlob => {
      const data = this.queuePrev()
      if (!data) return
      const sq = data.find(d => d.song_id === imageBlob.songId)
      if (!sq) return
      sq.image = URL.createObjectURL(imageBlob.blob)
      this.queuePrev.set([...data])
    });
  }

  clickOnPrev(sid: string) {
    this.router.navigate(["song", sid])
  }

  ngOnDestroy(): void {
    this.queuePrev$?.unsubscribe()
  }

  sort() {
    this.asc.set(this.asc() * -1)
  }

  toggleHide() {
    this.hidden.set(!this.hidden())
  }

  hideQueue(event: MouseEvent, sid: string) {
    event.stopPropagation();
    const queue = this.queuePrev()
    if (!queue) return
    const song = queue.find(q => q.song_id === sid)
    if (!song) return;
    song.hidden = !song.hidden
    this.queuePrev.set([...queue])
  }
}
