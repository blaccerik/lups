import {Routes} from '@angular/router';
import {HomeComponent} from "./components/home/home.component";
import {DisplayComponent} from "./components/display/display.component";
import {authGuard} from "./guards/auth.guard";
import {RedirectComponent} from "./components/redirect/redirect.component";

export const routes: Routes = [
  {path: '', component: HomeComponent, canActivate: [authGuard]},
  {path: 'song/:song_id', component: DisplayComponent, canActivate: [authGuard]},
  {path: 'redirect', component: RedirectComponent},
  {path: '**', redirectTo: '', pathMatch: 'full' },
];
