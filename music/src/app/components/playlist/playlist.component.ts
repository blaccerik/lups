import {Component, inject} from '@angular/core';
import {Router, RouterLink} from "@angular/router";
import {routes} from "../../app.routes";

@Component({
  selector: 'app-playlist',
  standalone: true,
  imports: [
    RouterLink
  ],
  templateUrl: './playlist.component.html',
  styleUrl: './playlist.component.scss'
})
export class PlaylistComponent {
  router = inject(Router)

  go() {
    this.router.navigate(["song", "erik"])
  }
  go2() {
    this.router.navigate(["song", "erik2"])
  }
}
