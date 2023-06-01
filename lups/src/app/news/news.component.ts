import { Component } from '@angular/core';

interface News {
  title: string;
  link: string;
  img_path: string;
  type: string;
}

@Component({
  selector: 'app-news',
  templateUrl: './news.component.html',
  styleUrls: ['./news.component.scss']
})
export class NewsComponent {



  news: News[] = [
    {title: "Politsei tormab kuriteopaika pärast segadust", link: "", img_path: "assets/news/1.jpg", type: "euro_symbol"},
    {title: "Võimud reageerivad kuriteopaigale kahtlaste tegevuste raportite taustal", link: "", img_path: "assets/news/2.jpg", type: "pets"},
    {title: "Uudis: Politsei uurib kuriteopaika, samal ajal kogukond seisab hämmingus", link: "", img_path: "assets/news/3.jpg", type: "shopping_cart"},
    {title: "Õiguskaitseorganid asuvad kuriteopaiga juurde pärast šokeerivat avastust", link: "", img_path: "assets/news/4.jpg", type: "shopping_cart"},
    {title: "Kuriteopaik suletud, kui politsei alustab uurimist", link: "", img_path: "assets/news/5.jpg", type: "euro_symbol"},
    {title: "Võimud tungivad kuriteopaika otsima vihjeid", link: "", img_path: "assets/news/6.jpg", type: "euro_symbol"},
    {title: "Politsei kohalolek kuriteopaigal tugevnenud; uurimine käib", link: "", img_path: "assets/news/7.jpg", type: "track_changes"},
  ];
}
