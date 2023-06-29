import { Component } from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../services/user-info.service";
import {Router} from "@angular/router";


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
    {text: "Tõnu", link: "/chat"},
    {text: "Raha", link: ""},
    {text: "Uudised", link: "/news"},
    {text: "Naised", link: ""},
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
