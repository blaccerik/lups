import {Component} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {Router} from "@angular/router";
import {UserInfoService} from "../../services/user-info.service";


interface Section {
  text: string;
  isSeen?: boolean;
  link?: string;
  id?: number;
  parentId?: number;
  // hasChildren?: boolean;
  // width?: number;
}

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  sections: Section[] = [
    {text: "Uudised", id: 1, link: "/news"},

    {text: "Erakond", id: 2, isSeen: false},
    {text: "Väärtused", parentId: 2, isSeen: false, link: "/promises"},

    {text: "Meelelahutus", id: 3, isSeen: false},
    {text: "Lõuend", parentId: 3, isSeen: false, link: "/place"},
    {text: "Vambolai", parentId: 3, isSeen: false, link: "/chat"},
  ]


  constructor(public readonly authService: OAuthService,
              public readonly userInfoService: UserInfoService,
              private readonly router: Router) {
  }

  isMenuOpen = false;

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  login() {
    this.isMenuOpen = false;
    // Store the original URL in local storage before initiating the login
    localStorage.setItem('originalUrl', window.location.pathname);
    this.authService.initLoginFlow('google');
  }

  logout() {
    this.isMenuOpen = false;
    this.authService.revokeTokenAndLogout().then(() => {
      this.router.navigate([""])
    })
  }


  home() {
    this.isMenuOpen = false;
    this.router.navigate([""])
  }

  go(currentSection: Section) {
    if (currentSection.link) {
      this.isMenuOpen = false;
      for (const section of this.sections) {
        if (section.isSeen !== undefined) {
          section.isSeen = false
        }
      }
      this.router.navigate([currentSection.link])
      return
    }
    if (currentSection.id) {
      currentSection.isSeen = !currentSection.isSeen
      for (const section of this.sections) {
        if (section.parentId == currentSection.id) {
          section.isSeen = !section.isSeen
        }
      }
    }
  }
}
