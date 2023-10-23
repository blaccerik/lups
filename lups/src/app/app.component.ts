import { Component } from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "./services/user-info.service";
import {Router} from "@angular/router";

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent {
  title = 'lups';
  constructor(private oauthService: OAuthService,
              private userInfoService: UserInfoService,
              private router: Router
  ) {
    this.oauthService.configure({
      issuer: 'https://accounts.google.com',
      strictDiscoveryDocumentValidation: false,
      redirectUri: window.location.origin,
      clientId: '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com',
      scope: 'openid profile email',
      showDebugInformation: true,
    });
    this.oauthService.loadDiscoveryDocumentAndTryLogin().then((a) => {
      console.log("disc",a)
      if (this.oauthService.hasValidIdToken()) {
        this.oauthService.loadUserProfile().then((r: any) => {
          this.userInfoService.userName = r.info.name
          this.userInfoService.picture = r.info.picture
          this.userInfoService.googleId = r.info.sub
          const url = localStorage.getItem("originalUrl")
          if (url) {
            localStorage.removeItem("originalUrl")
            this.router.navigate([url]).then(r => {
              console.log(r)
            })
          }

        }).catch((error: any) => {
          console.log("catch")
          console.log("error", error)
        })
      }
    });
  }
}
