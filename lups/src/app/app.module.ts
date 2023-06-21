import { NgModule } from '@angular/core';
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
import {ChatService} from "./services/chat.service";
import {HttpClientModule} from "@angular/common/http";
import { LoginComponent } from './login/login.component';

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
    LoginComponent,
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    AppRoutingModule,
    CommonModule,
    MatIconModule,
    FormsModule,
    HttpClientModule
  ],
  exports: [],
  providers: [
    ChatService
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
