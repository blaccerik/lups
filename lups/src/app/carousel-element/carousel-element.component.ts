import { Component } from '@angular/core';
import {animate, state, style, transition, trigger} from "@angular/animations";

@Component({
  selector: 'app-carousel-element',
  templateUrl: './carousel-element.component.html',
  styleUrls: ['./carousel-element.component.scss'],
  animations: [
    trigger('moveElement', [
      state('left', style({ transform: 'translateX(-50px)' })),
      state('right', style({ transform: 'translateX(0)' })),
      transition('left => right', animate('0ms')),
      transition('right => left', animate('500ms')),
    ]),
  ],
})
export class CarouselElementComponent {
  elementState = 'left';

  ngOnInit() {
    // Example: Move the element every 3 seconds
    setInterval(() => {
      if (this.elementState === 'right') {
        this.elementState = 'left';
      }
    }, 3000);
  }

  teleportBack() {
    this.elementState = 'right';
  }
}
