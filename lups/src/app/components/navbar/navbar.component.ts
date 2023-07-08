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
}

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  sections: Section[] = [
    {text: "Vestlused", id: 1, isSeen: true, hasChildren: true },
    {text: "Vambola", parentId: 1, isSeen: false, link: "/chat" },
    {text: "Test", id: 2, isSeen: true, link: "/test" },
    {text: "Sündmused", id: 3, isSeen: true, hasChildren: true },
    {text: "Suvepüks", parentId: 3, isSeen: false, link: "/suvepyks"},
    {text: "Carlos", parentId: 3, isSeen: false, link: "carlos" },
  ]



  constructor(public readonly authService: OAuthService,
              public readonly userInfoService: UserInfoService,
              private readonly router: Router) {}

  isMenuOpen = false;

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  login() {
    this.authService.initLoginFlow('google');
  }

  logout() {
    this.authService.revokeTokenAndLogout().then(() => {
      this.router.navigate([""])
    })
  }

  shouldDisplay(section: Section): string {
    // if (window.innerWidth <= 800 && section.menu && section.isOpen) {
    //   return "block"
    // }
    return "none"
  }

  go(parent: Section) {
    if (parent.link) {
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
