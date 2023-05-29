import { Component } from '@angular/core';

@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.scss']
})
export class TestComponent {
  images = [
    '1.jpg',
    '2.jpg',
    '3.jpg',
    '4.jpg',
    '5.jpg',
    '6.jpg',
    '7.png',
  ];

  images2 = [
    {path: 'https://source.unsplash.com/800x600/?nature'},
    {path: 'https://source.unsplash.com/800x600/?car'},
    {path: 'https://source.unsplash.com/800x600/?moto'},
    {path: 'https://source.unsplash.com/800x600/?fantasy'},
  ]

  imagePath = 'assets/wheel/';

  isDragging = false;
  startClientX = 0;
  scrollDistance = 0;

  // pauseScroll() {
  //   const imageContainer = document.querySelector('.image-container') as HTMLElement;
  //   imageContainer.style.animationPlayState = 'paused';
  // }
  //
  // resumeScroll() {
  //   const imageContainer = document.querySelector('.image-container') as HTMLElement;
  //   imageContainer.style.animationPlayState = 'running';
  // }
  //
  // startScroll(event: MouseEvent) {
  //   this.isDragging = true;
  //   this.startClientX = event.clientX;
  //   this.scrollDistance = 0;
  //   document.addEventListener('mousemove', this.onMouseMove.bind(this));
  // }
  //
  // // stopScroll() {
  // //   this.isDragging = false;
  // //   document.removeEventListener('mousemove', this.onMouseMove.bind(this));
  // // }
  //
  // scrollImages(event: MouseEvent) {
  //   if (this.isDragging) {
  //     const movementX = event.clientX - this.startClientX;
  //     this.scrollDistance += movementX;
  //     this.startClientX = event.clientX;
  //
  //     const imageContainer = document.querySelector('.image-container') as HTMLElement;
  //     const currentScroll = imageContainer.scrollLeft;
  //     imageContainer.scrollLeft = currentScroll - movementX;
  //   }
  // }
}
