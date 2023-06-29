import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {HomeComponent} from "./home/home.component";
import {NewsComponent} from "./news/news.component";
import {SingleNewsComponent} from "./news/single-news/single-news.component";
import {ChatComponent} from "./chat/chat.component";
import {TestComponent} from "./test/test.component";

const routes: Routes = [
  { path: '', component: HomeComponent},
  { path: "chat", component: ChatComponent},
  { path: "news", component: NewsComponent},
  { path: "news/:id", component: SingleNewsComponent},
  { path: "test", component: TestComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
