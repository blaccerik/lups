import { Routes } from '@angular/router';
import {PromisesComponent} from "./components/promises/promises.component";
import {HomeComponent} from "./components/home/home.component";
import {PlaceComponent} from "./components/place/place.component";
import {SingleNewsComponent} from "./components/news/single-news/single-news.component";
import {CreateNewsComponent} from "./components/news/create-news/create-news.component";
import {AllNewsComponent} from "./components/news/all-news/all-news.component";
import {ChatComponent} from "./components/chat/chat.component";
import {FamilyFeudComponent} from "./components/family-feud/family-feud.component";
import {AdminboardComponent} from "./components/family-feud/adminboard/adminboard.component";
import {GameboardComponent} from "./components/family-feud/gameboard/gameboard.component";
import {authGuard} from "./guards/auth.guard";

export const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: "chat", component: ChatComponent},
  {path: "chat/:id", component: ChatComponent},
  {path: "promises", component: PromisesComponent},
  {path: "news", component: AllNewsComponent},
  {path: "news/create", component: CreateNewsComponent},
  {path: "news/:id", component: SingleNewsComponent},
  // {path: "test", component: TestComponent},
  {path: "place", component: PlaceComponent},
  {path: "familyfeud", component: FamilyFeudComponent},
  {path: "familyfeud/:id", component: GameboardComponent},
  {path: "familyfeud/edit/:id", component: AdminboardComponent, canActivate: [authGuard]}
];
