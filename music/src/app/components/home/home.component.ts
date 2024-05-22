import {Component, inject, OnDestroy, signal} from '@angular/core';
import {MatIcon} from "@angular/material/icon";
import {MatToolbar} from "@angular/material/toolbar";
import {MatIconButton} from "@angular/material/button";
import {MatSlider, MatSliderThumb} from "@angular/material/slider";
import {FormsModule} from "@angular/forms";
import {PlayerComponent} from "../player/player.component";
import {DisplayComponent} from "../display/display.component";
import {MusicService, PreviousSongQueue} from "../../services/music.service";
import {Subscription} from "rxjs";
import {NgForOf} from "@angular/common";
import {Router} from "@angular/router";

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [
    MatIcon,
    MatToolbar,
    MatIconButton,
    MatSlider,
    MatSliderThumb,
    FormsModule,
    PlayerComponent,
    DisplayComponent,
    NgForOf
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent implements OnDestroy {
  musicService = inject(MusicService)
  router = inject(Router)
  queuePrev$: Subscription | undefined
  previous = signal<null | PreviousSongQueue[]>(null)

  constructor() {
    this.queuePrev$ = this.musicService.getQueuePrev().subscribe(
      previousSongQueue => {
        this.previous.set(previousSongQueue)
      }
    )
  }

  clickOnPrev(sid: string) {
    this.router.navigate(["song", sid])
  }

  ngOnDestroy(): void {
    this.queuePrev$?.unsubscribe()
  }
}
