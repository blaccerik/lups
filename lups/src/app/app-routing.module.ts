import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import {HomeComponent} from "./components/home/home.component";
import {NewsComponent} from "./components/news/news.component";
import {SingleNewsComponent} from "./components/news/single-news/single-news.component";
import {ChatComponent} from "./components/chat/chat.component";
import {TestComponent} from "./components/test/test.component";
import {PromisesComponent} from "./components/promises/promises.component";

const routes: Routes = [
  { path: '', component: HomeComponent},
  { path: "chat", component: ChatComponent},
  { path: "news", component: NewsComponent},
  { path: "promises", component: PromisesComponent },
  { path: "news/:id", component: SingleNewsComponent},
  { path: "test", component: TestComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
