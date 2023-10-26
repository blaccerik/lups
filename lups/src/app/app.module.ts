import {NgModule} from '@angular/core';
import {BrowserModule} from '@angular/platform-browser';

import {AppRoutingModule} from './app-routing.module';
import {AppComponent} from './app.component';
import {CommonModule, NgOptimizedImage} from "@angular/common";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import {TestComponent} from './components/test/test.component';
import {HomeComponent} from './components/home/home.component';
import {CreateNewsComponent} from './components/news/create-news/create-news.component';
import {MatIconModule} from '@angular/material/icon';
import {MiniNewsComponent} from './components/home/mini-news/mini-news.component';
import {SingleNewsComponent} from './components/news/single-news/single-news.component';
import {ChatComponent} from './components/chat/chat.component';
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {HTTP_INTERCEPTORS, HttpClientModule} from "@angular/common/http";
import {OAuthModule, OAuthService, OAuthStorage} from 'angular-oauth2-oidc';
import {UserInfoService} from "./services/user-info.service";
import {AuthInterceptor} from "./interceptors/auth.interceptor";
import {NavbarComponent} from "./components/navbar/navbar.component";
import {PromisesComponent} from './components/promises/promises.component';
import {PlaceComponent} from './components/place/place.component';
import {PlaceService} from "./services/place.service";
import {SocketIoConfig, SocketIoModule} from "ngx-socket-io";
import {NgxImageZoomModule} from 'ngx-image-zoom';
import {NotLoggedInPopupComponent} from './services/not-logged-in-popup/not-logged-in-popup.component';
import {HelpDialogComponent} from './components/place/help-dialog/help-dialog.component';
import {MatDialogModule, MatDialogRef} from "@angular/material/dialog";
import {AllNewsComponent} from './components/news/all-news/all-news.component';
import {InfiniteScrollModule} from "ngx-infinite-scroll";
import {environment} from '../environments/environment';
import {MatButtonModule} from "@angular/material/button";
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatTabsModule} from "@angular/material/tabs";
import {MatSelectModule} from "@angular/material/select";
import {MatDividerModule} from "@angular/material/divider";
import {MatInputModule} from "@angular/material/input";
import {MatToolbarModule} from "@angular/material/toolbar";
import {MatMenuModule} from "@angular/material/menu";
import {MatButtonToggleModule} from "@angular/material/button-toggle";
import {MatChipsModule} from "@angular/material/chips";
import {MatSidenavModule} from "@angular/material/sidenav";
import {MatTooltipModule} from "@angular/material/tooltip";
import {MatCardModule} from "@angular/material/card";

const socketIoConfig: SocketIoConfig = {
  url: environment.wsUrl, // Update this with your Flask-SocketIO server URL
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
    AllNewsComponent
  ],
  imports: [
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
    InfiniteScrollModule,
    MatButtonModule,
    MatFormFieldModule,
    MatTabsModule,
    MatIconModule,
    MatFormFieldModule,
    MatSelectModule,
    BrowserAnimationsModule,
    MatDividerModule,
    ReactiveFormsModule,
    MatButtonModule,
    MatInputModule,
    MatToolbarModule,
    MatMenuModule,
    MatButtonToggleModule,
    MatDialogModule,
    MatChipsModule,
    MatSidenavModule,
    MatTooltipModule,
    MatCardModule,
    NgOptimizedImage
  ],
  exports: [],
  providers: [
    OAuthService,
    PlaceService,
    {
      provide: MatDialogRef,
      useValue: {}
    },
    {provide: OAuthStorage, useValue: localStorage},
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {
}
