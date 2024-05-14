import {Component, inject} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {MatIconButton} from "@angular/material/button";
import {MatIcon} from "@angular/material/icon";
import {NgForOf} from "@angular/common";
import {Song} from "../../services/audio.service";
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
  song = this.musicService.song.asReadonly()

  songs: Song[] = [
    {
      id: "",
      title: "15",
      artist: null,
      src: "https://download.samplelib.com/mp3/sample-15s.mp3"
    },
    {
      id: "",
      title: "sssss6",
      artist: null,
      src: "https://filesamples.com/samples/audio/mp3/sample2.mp3"
    },
    {
      id: "",
      title: "9",
      artist: null,
      src: "https://download.samplelib.com/mp3/sample-9s.mp3"
    }
  ]

  clickSong(song: Song) {
    this.musicService.song.set(song)
  }
}
