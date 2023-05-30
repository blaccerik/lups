import { Component } from '@angular/core';

@Component({
  selector: 'app-ads',
  templateUrl: './ads.component.html',
  styleUrls: ['./ads.component.scss']
})
export class AdsComponent {
  images = [
    '1.png',
    '2.png',
    '3.png'
  ];

  path = "assets/ads/"
}
