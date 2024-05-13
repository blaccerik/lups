import {Component} from '@angular/core';
import {MatIcon} from "@angular/material/icon";
import {MatToolbar} from "@angular/material/toolbar";
import {MatIconButton} from "@angular/material/button";
import {MatSlider, MatSliderThumb} from "@angular/material/slider";
import {FormsModule} from "@angular/forms";
import {PlayerComponent} from "../player/player.component";
import {DisplayComponent} from "../display/display.component";

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
    DisplayComponent
  ],
  templateUrl: './home.component.html',
  styleUrl: './home.component.scss'
})
export class HomeComponent {
  // urls = [
  //   "https://download.samplelib.com/mp3/sample-3s.mp3",
  //   // "https://file-examples.com/wp-content/storage/2017/11/file_example_MP3_1MG.mp3",
  //   "https://ia801504.us.archive.org/3/items/EdSheeranPerfectOfficialMusicVideoListenVid.com/Ed_Sheeran_-_Perfect_Official_Music_Video%5BListenVid.com%5D.mp3",
  //   "https://ia801609.us.archive.org/16/items/nusratcollection_20170414_0953/Man%20Atkiya%20Beparwah%20De%20Naal%20Nusrat%20Fateh%20Ali%20Khan.mp3",
  //   "https://ia801503.us.archive.org/15/items/TheBeatlesPennyLane_201805/The%20Beatles%20-%20Penny%20Lane.mp3",
  // ]
  // audio = new Audio();
  // musicLength: string = '0:00';
  // duration: number = 1;
  // currentTime: string = '0:00';
  // musicList: Music[] = [];
  //
  // displayedColumns: string[] = ['title', 'artist', 'album'];
  // trackPointer: number = 0;
  // currentMusic: Music = {
  //   album: "",
  //   title: "",
  //   artist: "",
  //   url: ""
  // }
  //
  // play() {
  //   const url = "https://download.samplelib.com/mp3/sample-3s.mp3"
  //   this.audio.src = url
  //   this.audio.play()
  // }
  //
  // pause() {
  //   this.audio.pause();
  // }

}
