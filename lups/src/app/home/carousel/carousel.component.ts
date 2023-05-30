import { Component } from '@angular/core';

interface Cell {
  position: number;
  img: string;
  user: string;
  header: string;
  text: string;
}

@Component({
  selector: 'app-carousel',
  templateUrl: './carousel.component.html',
  styleUrls: ['./carousel.component.scss']
})
export class CarouselComponent {
  cells: Cell[] = [];
  cellSize = 400;
  isButtonDisabled: boolean = false;

  ngOnInit(): void {

    // might break
    let x = 7

    for (let i = 0; i < x; i++) {
      const cell: Cell = {
        position: (i - 2) * this.cellSize,
        img: this.images[i],
        user: "Erik Kalle",
        header: "Kas carlos on kole?",
        text: "Muidugi"
      }
      this.cells.push(cell)
    }
  }

  moveRight(): void {
    if (this.isButtonDisabled) {
      return;
    }

    this.disableButton();

    for (let i = 0; i < this.cells.length; i++) {
      const cell: Cell = this.cells[i];
      cell.position += this.cellSize;
      if (cell.position > this.cellSize * 4) {
        cell.position = this.cellSize * -2;
      }
    }
  }

  moveLeft(): void {
    if (this.isButtonDisabled) {
      return;
    }

    this.disableButton();

    for (let i = 0; i < this.cells.length; i++) {
      const cell: Cell = this.cells[i];
      cell.position -= this.cellSize;
      if (cell.position < this.cellSize * -2) {
        cell.position = this.cellSize * 4;
      }
    }
  }

  getTransition(position: number): string {
    if (position == -2 * this.cellSize || position == this.cellSize * 4) {
      return 'none'
    }
    return 'transform 1s ease';
  }

  disableButton(): void {
    this.isButtonDisabled = true;
    setTimeout(() => {
      this.isButtonDisabled = false;
    }, 1000); // Disable button for 1 second
  }

  images = [
    '1.jpg',
    '2.jpg',
    '3.jpg',
    '4.jpg',
    '5.jpg',
    '6.jpg',
    '7.png',
  ];

  imagePath = 'assets/wheel/';
}
