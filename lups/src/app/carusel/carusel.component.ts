import {Component, OnInit} from '@angular/core';

interface Cell {
  position: number;
  data: string;
}

@Component({
  selector: 'app-carusel',
  templateUrl: './carusel.component.html',
  styleUrls: ['./carusel.component.scss']
})
export class CaruselComponent {

  cells: Cell[] = [];
  cellSize = 400;
  isButtonDisabled: boolean = false;

  ngOnInit(): void {

    // might break
    let x = 7

    for (let i = 0; i < x; i++) {
      const cell: Cell = {position: (i - 2) * this.cellSize, data: this.images[i]}
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

  currentIndex = 0;
  previousIndex = this.calculatePreviousIndex();
  nextIndex = this.calculateNextIndex();

  rotateNext(): void {
    this.currentIndex = this.nextIndex;
    this.nextIndex = this.calculateNextIndex();
    this.previousIndex = this.calculatePreviousIndex();
  }

  rotatePrevious(): void {
    this.currentIndex = this.previousIndex;
    this.nextIndex = this.calculateNextIndex();
    this.previousIndex = this.calculatePreviousIndex();
  }

  private calculateNextIndex(): number {
    return (this.currentIndex + 1) % this.images.length;
  }

  private calculatePreviousIndex(): number {
    return (this.currentIndex - 1 + this.images.length) % this.images.length;
  }
}
