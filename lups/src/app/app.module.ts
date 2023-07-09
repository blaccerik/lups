import {NgModule} from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import {CommonModule} from "@angular/common";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import { TestComponent } from './components/test/test.component';
import { HomeComponent } from './components/home/home.component';
import { NewsComponent } from './components/news/news.component';
import { MatIconModule} from '@angular/material/icon';
import { MiniNewsComponent } from './components/home/mini-news/mini-news.component';
import { SingleNewsComponent } from './components/news/single-news/single-news.component';
import { ChatComponent } from './components/chat/chat.component';
import {FormsModule} from "@angular/forms";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import {OAuthModule, OAuthService, OAuthStorage} from 'angular-oauth2-oidc';
import {UserInfoService} from "./services/user-info.service";
import {AuthInterceptor} from "./interceptors/auth.interceptor";
import {NavbarComponent} from "./components/navbar/navbar.component";
import { PromisesComponent } from './components/promises/promises.component';

@NgModule({
  declarations: [
    NavbarComponent,
    AppComponent,
    TestComponent,
    HomeComponent,
    NewsComponent,
    MiniNewsComponent,
    SingleNewsComponent,
    ChatComponent,
    PromisesComponent,
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
          this.userInfoService.userName = r.info.name
          this.userInfoService.picture = r.info.picture
        })
      }
    });
  }
}
