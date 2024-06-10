import {Component, inject, OnDestroy, signal} from '@angular/core';
import {MusicService, PreviousSongQueue} from "../../services/music.service";
import {mergeMap, Subscription, switchMap, tap} from "rxjs";
import {Router} from "@angular/router";
import {NgClass, NgForOf, NgOptimizedImage} from "@angular/common";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    NgForOf,
    NgOptimizedImage,
    NgClass
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnDestroy {
  musicService = inject(MusicService)
  router = inject(Router)
  queuePrev$: Subscription | undefined
  previous = signal<null | PreviousSongQueue[]>(null)
  img: any

  constructor() {
    this.queuePrev$ = this.musicService.getQueuePrev().pipe(
      tap(data => this.previous.set(data)),
      switchMap(data => data), // flatten the array of items into individual items
      mergeMap(item => this.musicService.getSongImage(item.song_id)) // process each item as soon as it's emitted
    ).subscribe(image => {
      this.img = URL.createObjectURL(image)

      // todo not sure if calls different endpoints and gets different images
      console.log(this.img)
    });
  }

  clickOnPrev(sid: string) {
    this.router.navigate(["song", sid])
  }

  ngOnDestroy(): void {
    this.queuePrev$?.unsubscribe()
  }

  getImage(sid: string) {
    console.log(sid)
    // this.musicService.getSongImage(sid).subscribe(
    //   value => {
    //     console.log(value.size)
    //   })
    return "ew"
  }
}
