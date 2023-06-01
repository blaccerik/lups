import { Component } from '@angular/core';
import {Router} from "@angular/router";

interface News {
  title: string;
  link: string;
  img_path: string;
  type: string;
}

@Component({
  selector: 'app-mini-news',
  templateUrl: './mini-news.component.html',
  styleUrls: ['./mini-news.component.scss']
})
export class MiniNewsComponent {

  constructor(private router: Router) { }

  news: News[] = [
    {title: "Politsei tormab kuriteopaika pärast segadust", link: "2323", img_path: "assets/news/1.jpg", type: "euro_symbol"},
    {title: "Võimud reageerivad kuriteopaigale kahtlaste tegevuste raportite taustal", link: "1", img_path: "assets/news/2.jpg", type: "pets"},
    {title: "Uudis: Politsei uurib kuriteopaika, samal ajal kogukond seisab hämmingus", link: "333", img_path: "assets/news/3.jpg", type: "shopping_cart"},
    {title: "Õiguskaitseorganid asuvad kuriteopaiga juurde pärast šokeerivat avastust", link: "ghg", img_path: "assets/news/4.jpg", type: "shopping_cart"},
    {title: "Kuriteopaik suletud, kui politsei alustab uurimist", link: "33", img_path: "assets/news/5.jpg", type: "euro_symbol"},
    {title: "Võimud tungivad kuriteopaika otsima vihjeid", link: "fgfgfg", img_path: "assets/news/6.jpg", type: "euro_symbol"},
    {title: "Politsei kohalolek kuriteopaigal tugevnenud; uurimine käib", link: "4343", img_path: "assets/news/7.jpg", type: "track_changes"},
  ];

  go(news: News) {
    this.router.navigate(["news/" + news.link])
  }
}
