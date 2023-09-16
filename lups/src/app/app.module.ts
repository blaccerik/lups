import {NgModule} from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {CommonModule} from "@angular/common";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import { TestComponent } from './components/test/test.component';
import { HomeComponent } from './components/home/home.component';
import { CreateNewsComponent } from './components/news/create-news/create-news.component';
import { MatIconModule} from '@angular/material/icon';
import { MiniNewsComponent } from './components/home/mini-news/mini-news.component';
import { SingleNewsComponent } from './components/news/single-news/single-news.component';
import { ChatComponent } from './components/chat/chat.component';
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import {OAuthModule, OAuthService, OAuthStorage} from 'angular-oauth2-oidc';
import {UserInfoService} from "./services/user-info.service";
import {AuthInterceptor} from "./interceptors/auth.interceptor";
import {NavbarComponent} from "./components/navbar/navbar.component";
import { PromisesComponent } from './components/promises/promises.component';
import { PlaceComponent } from './components/place/place.component';
import {PlaceService} from "./services/place.service";
import {SocketIoConfig, SocketIoModule} from "ngx-socket-io";
import { NgxImageZoomModule } from 'ngx-image-zoom';
import { NotLoggedInPopupComponent } from './services/not-logged-in-popup/not-logged-in-popup.component';
import { HelpDialogComponent } from './services/help-dialog/help-dialog.component';
import {MatDialogModule, MatDialogRef} from "@angular/material/dialog";
import { AllNewsComponent } from './components/news/all-news/all-news.component';
import {InfiniteScrollModule} from "ngx-infinite-scroll";

const socketIoConfig: SocketIoConfig = {
  url: 'ws://localhost:5000/place', // Update this with your Flask-SocketIO server URL
  options: {},
};

@NgModule({
  declarations: [
    NavbarComponent,
    AppComponent,
    TestComponent,
    HomeComponent,
    CreateNewsComponent,
    MiniNewsComponent,
    SingleNewsComponent,
    ChatComponent,
    PromisesComponent,
    PlaceComponent,
    NotLoggedInPopupComponent,
    HelpDialogComponent,
    AllNewsComponent,
  ],
    imports: [
        SocketIoModule.forRoot(socketIoConfig), // Add this line
        BrowserAnimationsModule,
        BrowserModule,
        NgxImageZoomModule,
        AppRoutingModule,
        CommonModule,
        MatIconModule,
        FormsModule,
        MatDialogModule,
        HttpClientModule,
        ReactiveFormsModule,
        OAuthModule.forRoot(),
        InfiniteScrollModule
    ],
  exports: [],
  providers: [
    OAuthService,
    PlaceService,
    {
      provide: MatDialogRef,
      useValue: {}
    },
    { provide: OAuthStorage, useValue: localStorage },
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
  constructor(private oauthService: OAuthService,
              private userInfoService: UserInfoService,

  ) {
    this.oauthService.configure({
      issuer: 'https://accounts.google.com',
      strictDiscoveryDocumentValidation: false,
      redirectUri: window.location.origin,
      clientId: '437646142767-evt2pt3tn4pbrjcea6pd71quq07h82j7.apps.googleusercontent.com',
      scope: 'openid profile email',
      showDebugInformation: true,
    });
    this.oauthService.setStorage(localStorage);
    this.oauthService.loadDiscoveryDocumentAndTryLogin().then((a) => {
      if (this.oauthService.hasValidIdToken()) {
        this.oauthService.loadUserProfile().then((r: any) => {
          this.userInfoService.userName = r.info.name
          this.userInfoService.picture = r.info.picture
          this.userInfoService.googleId = r.info.sub
        }).catch((r: any) => {
          console.log("catch")
          console.log(this.oauthService.hasValidIdToken())
          console.log(a)
          console.log(r)
        })
      }
    });
  }
}
