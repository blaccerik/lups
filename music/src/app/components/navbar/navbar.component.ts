import {Component, inject} from '@angular/core';
import {GoogleApiService} from "../../services/google-api.service";

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.scss'
})
export class NavbarComponent {
  googleApiService = inject(GoogleApiService)

  signOut() {
    this.googleApiService.signOut()
  }
}
