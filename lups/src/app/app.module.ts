import {NgModule} from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CaruselComponent } from './carusel/carusel.component';
import {CommonModule} from "@angular/common";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import { CarouselElementComponent } from './carousel-element/carousel-element.component';
import { TestComponent } from './test/test.component';
import { PonyComponent } from './pony/pony.component';
import { CarouselComponent } from './home/carousel/carousel.component';
import { AdsComponent } from './home/ads/ads.component';
import { HomeComponent } from './home/home.component';
import { NavbarComponent } from "./navbar/navbar.component";
import { NewsComponent } from './news/news.component';
import { MatIconModule} from '@angular/material/icon';
import { MiniNewsComponent } from './home/mini-news/mini-news.component';
import { SingleNewsComponent } from './news/single-news/single-news.component';
import { ChatComponent } from './chat/chat.component';
import {FormsModule} from "@angular/forms";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import {OAuthModule, OAuthService, OAuthStorage} from 'angular-oauth2-oidc';
import {UserInfoService} from "./services/user-info.service";
import {AuthInterceptor} from "./auth.interceptor";

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    CaruselComponent,
    CarouselElementComponent,
    TestComponent,
    PonyComponent,
    CarouselComponent,
    AdsComponent,
    HomeComponent,
    NewsComponent,
    MiniNewsComponent,
    SingleNewsComponent,
    ChatComponent,
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    AppRoutingModule,
    CommonModule,
    MatIconModule,
    FormsModule,
    HttpClientModule,
    OAuthModule.forRoot()
  ],
  exports: [],
  providers: [
    OAuthService,
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
    this.oauthService.loadDiscoveryDocumentAndTryLogin().then(() => {
      if (this.oauthService.hasValidIdToken()) {
        this.oauthService.loadUserProfile().then((r: any) => {
          console.log(r)
          this.userInfoService.setUserName(r.info.name)
        })
      }
    });
  }
}
