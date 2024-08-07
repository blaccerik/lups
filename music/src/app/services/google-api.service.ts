import {Injectable, signal} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";


export interface UserInfo {
  info: {
    sub: string,
    name: string,
    picture: string
  }
}

@Injectable({
  providedIn: 'root'
})
export class GoogleApiService {

  userinfo = signal<UserInfo>({
    info: {
      sub: "",
      name: "",
      picture: ""
    }
  })
  loggedIn = signal<null | boolean>(null)

  constructor(private oAuthService: OAuthService) {
    oAuthService.configure({
      issuer: 'https://accounts.google.com',
      strictDiscoveryDocumentValidation: false,
      redirectUri: window.location.origin,
      clientId: '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com',
      scope: 'openid profile email',
      showDebugInformation: true,
    });
    this.loggedIn.set(true)
    this.userinfo.set({
      info: {
        sub: "erik",
        name: "Moe Lester",
        picture: "https://lh3.googleusercontent.com/a/ACg8ocKgt_tbLy-UDAKIN31UV1yr_OqV6Z8pBboQDZ_isWZf3G_mUZI=s96-c"
      }
    })
    // oAuthService.loadDiscoveryDocument().then((e) => {
    //   oAuthService.tryLoginImplicitFlow().then((t) => {
    //     this.loggedIn.set(oAuthService.hasValidAccessToken())
    //     if (!oAuthService.hasValidAccessToken()) {
    //       oAuthService.initLoginFlow()
    //     } else {
    //       oAuthService.loadUserProfile().then((userProfile) => {
    //         this.userinfo.set(userProfile as UserInfo)
    //       })
    //     }
    //   })
    // })
  }

  signOut() {
    this.oAuthService.revokeTokenAndLogout().then(() => {
        this.oAuthService.initLoginFlow()
      }
    )
  }
}
