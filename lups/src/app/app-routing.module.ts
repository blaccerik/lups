import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {CarouselComponent} from "./home/carousel/carousel.component";
import {HomeComponent} from "./home/home.component";
import {NewsComponent} from "./news/news.component";
import {SingleNewsComponent} from "./news/single-news/single-news.component";

const routes: Routes = [
  { path: '', component: HomeComponent},
  { path: "news", component: NewsComponent},
  { path: "news/:id", component: SingleNewsComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
