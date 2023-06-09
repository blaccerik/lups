import { Component } from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {Router} from "@angular/router";
import {UserInfoService} from "../../services/user-info.service";


interface Section {
  text: string;
  isSeen: boolean;
  link?: string;
  id?: number;
  parentId?: number;
  hasChildren?: boolean;
  width?: number;
}

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  sections: Section[] = [
    {text: "Vestlused", id: 1, isSeen: true, hasChildren: true },
    {text: "Vambola", parentId: 1, isSeen: false, link: "/chat", width: 119},
    {text: "Väärtused", id: 2, isSeen: true, link: "/promises" },
    {text: "Sündmused", id: 3, isSeen: true, hasChildren: true },
    {text: "Suvepüks 2003", parentId: 3, isSeen: false, link: "/events/suvepyks", width: 159},
    {text: "Carlos", parentId: 3, isSeen: false, link: "/events/carlos", width: 100},
  ]



  constructor(public readonly authService: OAuthService,
              public readonly userInfoService: UserInfoService,
              private readonly router: Router) {}

  isMenuOpen = false;

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  login() {
    this.isMenuOpen = false;
    this.authService.initLoginFlow('google');
  }

  logout() {
    this.isMenuOpen = false;
    this.authService.revokeTokenAndLogout().then(() => {
      this.router.navigate([""])
    })
  }

  getWidth(n: any) {
    if (n) {
      return n + "px"
    }
    return "50px"
  }

  home() {
    this.isMenuOpen = false;
    this.router.navigate([""])
  }

  go(parent: Section) {
    if (parent.link) {
      this.isMenuOpen = false;
      this.router.navigate([parent.link])
      return
    }
    if (window.innerWidth <= 800 && parent.id) {
      parent.isSeen = !parent.isSeen
      for (const child of this.sections) {
        if (child.parentId == parent.id) {
          child.isSeen = !child.isSeen
        }
      }
    }
  }
}
