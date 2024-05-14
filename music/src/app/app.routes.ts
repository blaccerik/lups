import { Routes } from '@angular/router';
import {HomeComponent} from "./components/home/home.component";
import {SongComponent} from "./components/song/song.component";
import {DisplayComponent} from "./components/display/display.component";

export const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'song', component: DisplayComponent},
  {path: 'song/:song_id', component: DisplayComponent},
];
