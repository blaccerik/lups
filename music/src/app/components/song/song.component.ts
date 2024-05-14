import {Component, inject} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {MatIconButton} from "@angular/material/button";
import {MatIcon} from "@angular/material/icon";
import {NgForOf} from "@angular/common";
import {MusicService} from "../../services/music.service";

@Component({
  selector: 'app-song',
  standalone: true,
  imports: [
    MatDrawerContainer,
    MatDrawer,
    MatDrawerContent,
    MatIconButton,
    MatIcon,
    NgForOf
  ],
  templateUrl: './song.component.html',
  styleUrl: './song.component.scss'
})
export class SongComponent {
  private musicService = inject(MusicService)
  song = this.musicService.currentSong.asReadonly()
}
