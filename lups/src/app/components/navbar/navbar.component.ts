import { Component } from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {Router} from "@angular/router";
import {UserInfoService} from "../../services/user-info.service";


interface section {
  text: string;
  link: string;
}

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  sections: section[] = [
    {text: "Vambola", link: "/chat"},
    // {text: "Raha", link: ""},
    // {text: "Uudised", link: "/news"},
    // {text: "Naised", link: ""},
  ]

  constructor(public readonly authService: OAuthService,
              public readonly userInfoService: UserInfoService,
              private readonly router: Router) {}



  login() {
    this.authService.initLoginFlow('google');
  }

  logout() {
    this.authService.revokeTokenAndLogout().then(() => {
      this.router.navigate([""])
    })

  }
}
