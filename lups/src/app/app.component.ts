import {Component} from '@angular/core';
import {Router, RouterOutlet} from '@angular/router';
import {NavbarComponent} from "./components/navbar/navbar.component";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "./services/user-info.service";

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, NavbarComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'lups';

  constructor(private oauthService: OAuthService,
              private userInfoService: UserInfoService,
              private router: Router) {
    this.oauthService.configure({
      issuer: 'https://accounts.google.com',
      strictDiscoveryDocumentValidation: false,
      redirectUri: window.location.origin,
      clientId: '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com',
      scope: 'openid profile email',
      showDebugInformation: true,
    });
    this.oauthService.loadDiscoveryDocumentAndTryLogin().then((a) => {
      console.log("discovery", a)
      if (this.oauthService.hasValidIdToken()) {
        console.log("ID TOKEN IS VALID")
        this.oauthService.loadUserProfile().then((r: any) => {
          this.userInfoService.userName = r.info.name
          this.userInfoService.picture = r.info.picture
          this.userInfoService.googleId = r.info.sub
          const url = localStorage.getItem("originalUrl")
          if (url) {
            localStorage.removeItem("originalUrl")
            this.router.navigate([url])
          }

        }).catch((error: any) => {
          console.log("ERROR LOADING USER PROFILE")
          console.log("error", error)

          // // todo reimplement this
          localStorage.removeItem("id_token")
          sessionStorage.removeItem("id_token")
          this.oauthService.revokeTokenAndLogout().then(r => {
            this.router.navigate([""])
          }).catch(e => {
            console.log("very bad error", e)
          })
        })
      } else {
        console.log("ID TOKEN IS NOT VALID")
      }
    });
    // this.oauthService.setupAutomaticSilentRefresh();
  }
}
