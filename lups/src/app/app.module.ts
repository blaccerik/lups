import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { NavbarComponent } from './navbar/navbar.component';
import { CaruselComponent } from './carusel/carusel.component';
import {CommonModule} from "@angular/common";
import {BrowserAnimationsModule} from "@angular/platform-browser/animations";
import { CarouselElementComponent } from './carousel-element/carousel-element.component';
import { TestComponent } from './test/test.component';

@NgModule({
  declarations: [
    AppComponent,
    NavbarComponent,
    CaruselComponent,
    CarouselElementComponent,
    TestComponent
  ],
  imports: [
    BrowserAnimationsModule,
    BrowserModule,
    AppRoutingModule,
    CommonModule
  ],
  exports: [
    CaruselComponent
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
