import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CarouselComponent} from "./home/carousel/carousel.component";
import {HomeComponent} from "./home/home.component";

const routes: Routes = [
  { path: '', component: HomeComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
