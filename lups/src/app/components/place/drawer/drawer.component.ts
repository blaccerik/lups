import {Component, ElementRef, EventEmitter, Output, ViewChild} from '@angular/core';
import {MatIcon} from "@angular/material/icon";
import {MatMenu, MatMenuItem, MatMenuTrigger} from "@angular/material/menu";
import {NgForOf, NgIf, NgStyle} from "@angular/common";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MatDialog} from "@angular/material/dialog";
import {HelpDialogComponent} from "../help-dialog/help-dialog.component";

export interface Color {
  value: string
  text: string
  rgb: number[]
}

export interface Tool {
  selectedTool: string | null

  brushSize: number
  brushColor: Color
  brushMatrix: (string | null)[][]


  imgSize: number
  originalImage: string | null
  editedImage: string | null
  imageMatrix: (string | null)[][]
  // imageColors: (Color | null)[],

  shadows: boolean,
  names: boolean
}

@Component({
  selector: 'app-drawer',
  standalone: true,
  imports: [
    MatIcon,
    MatIcon,
    MatMenu,
    MatMenu,
    MatMenuItem,
    MatMenuItem,
    NgForOf,
    NgForOf,
    NgIf,
    NgIf,
    ReactiveFormsModule,
    ReactiveFormsModule,
    FormsModule,
    NgStyle,
    MatMenuTrigger
  ],
  templateUrl: './drawer.component.html',
  styleUrl: './drawer.component.scss'
})
export class DrawerComponent {
  ALPHA_CUTOFF = 50
  colors: Color[] = [
    {value: 'red', text: "punane", rgb: [255, 0, 0]},
    {value: 'green', text: "roheline", rgb: [0, 255, 0]},
    {value: 'blue', text: "sinine", rgb: [0, 0, 255]},
    {value: 'yellow', text: "kollane", rgb: [255, 255, 0]},
    {value: 'purple', text: "lilla", rgb: [255, 0, 255]},
    {value: 'orange', text: "oranž", rgb: [255, 165, 0]},
    {value: 'black', text: "must", rgb: [0, 0, 0]},
    {value: 'white', text: "valge", rgb: [255, 255, 255]},
  ];
  tool: Tool

  @Output() dataEvent = new EventEmitter<Tool>();


  constructor(private dialog: MatDialog) {
  }


  ngOnInit(): void {

    // set default values
    this.tool = {
      selectedTool: null,
      brushColor: this.colors[0],
      brushSize: 1,
      imgSize: 10,
      originalImage: null,
      editedImage: null,
      imageMatrix: [],
      brushMatrix: [[this.colors[0].value]],
      shadows: false,
      names: false
    }
  }


  @ViewChild('canvas', {static: true}) canvasRef: ElementRef;
  private context: CanvasRenderingContext2D | null;

  private updateImage() {
    if (!this.tool.originalImage) {
      return
    }
    const image = new Image();
    image.src = this.tool.originalImage
    image.onload = () => {
      const colors = this.imageToColors(image)
      this.tool.imageMatrix = colors
      this.tool.editedImage = this.createImage(colors)
      this.dataEvent.emit(this.tool)
    };
  }

  selectTool(tool: string) {
    if (this.tool.selectedTool === tool) {
      this.tool.selectedTool = null
    } else {
      this.tool.selectedTool = tool
    }
    this.dataEvent.emit(this.tool)
  }

  private updateBrush() {
    const size = this.tool.brushSize
    const colors: (string | null)[][] = new Array(size)
    for (let i = 0; i < size; i++) {
      colors[i] = new Array(size)
      for (let j = 0; j < size; j++) {
        colors[i][j] = this.tool.brushColor.value
      }
    }
    this.tool.brushMatrix = colors
    this.dataEvent.emit(this.tool)
  }

  increaseBrushSize() {
    if (this.tool.brushSize < 4) {
      this.tool.brushSize++
    }
    this.updateBrush()
  }

  decreaseBrushSize() {
    if (this.tool.brushSize > 1) {
      this.tool.brushSize--
    }
    this.updateBrush()
  }

  selectColor(color: Color) {
    this.tool.brushColor = color
    this.updateBrush()
  }

  increaseImageSize() {
    if (this.tool.imgSize < 19) {
      this.tool.imgSize++
    }
    this.updateImage()
  }

  decreaseImageSize() {
    if (this.tool.imgSize > 11) {
      this.tool.imgSize--
    }
    this.updateImage()
  }

  changeShadows() {
    this.dataEvent.emit(this.tool)
  }

  changeNames() {
    this.dataEvent.emit(this.tool)
  }

  @ViewChild('fileInput', {static: false}) fileInput: ElementRef;

  clearImage(event: Event) {
    event.stopPropagation();
    this.tool.originalImage = null
    this.tool.editedImage = null
    this.tool.imageMatrix = []
    this.selectedImage = null

    // Reset the value of the file input without triggering a click event
    this.fileInput.nativeElement.value = '';
    this.dataEvent.emit(this.tool)
  }

  selectedImage: string | ArrayBuffer | null = null;

  onFileSelected(event: any): void {
    const file = event.target.files[0];
    if (file) {
      this.loadImage(file);
    }
  }

  loadImage(file: File): void {
    const reader = new FileReader();
    reader.onload = () => {
      this.selectedImage = reader.result as string;
      this.tool.originalImage = this.selectedImage
      this.updateImage()
    };
    reader.readAsDataURL(file);
  }

  imageToColors(img: HTMLImageElement): (string | null)[][] {
    // Create an off-screen canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return []
    }

    const size = this.tool.imgSize

    // Set its dimension to the target size
    canvas.width = size;
    canvas.height = size;

    // Draw the source image into the off-screen canvas
    ctx.drawImage(img, 0, 0, size, size);

    // Get the image data from the canvas
    const imageData = ctx.getImageData(0, 0, size, size);

    // Access the pixel data array
    const pixelData = imageData.data;

    // Create an array to store RGB values
    const colors1d: (string | null)[] = []

    // Iterate through the pixel data array and extract RGB values
    for (let i = 0; i < pixelData.length; i += 4) {
      const red = pixelData[i];
      const green = pixelData[i + 1];
      const blue = pixelData[i + 2];
      const alpha = pixelData[i + 3]
      if (alpha < this.ALPHA_CUTOFF) {
        colors1d.push(null)
      } else {
        colors1d.push(this.closestColor([red, green, blue]).value)
      }
    }

    // convert to 2d array
    const colors: (string | null)[][] = new Array(size)
    for (let i = 0; i < size; i++) {
      colors[i] = new Array(size)
      for (let j = 0; j < size; j++) {
        colors[i][j] = colors1d[i + j * size]
      }
    }
    return colors
  }

  closestColor(targetColor: number[]): Color {
    const colors = this.colors.map(color => this.calculateDistance(color.rgb, targetColor));
    const index = colors.indexOf(Math.min(...colors))
    return this.colors[index];
  }

  private calculateDistance(color1: number[], color2: number[]): number {
    const squaredDifferences = color1.map((value, index) => (value - color2[index]) ** 2);
    const sumSquaredDifferences = squaredDifferences.reduce((acc, val) => acc + val, 0);
    return Math.sqrt(sumSquaredDifferences);
  }


  createImage(colors: (string | null)[][]) {
    // Create an off-screen canvas
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return ""
    }

    const size = this.tool.imgSize

    // Set the canvas dimensions
    canvas.width = size;
    canvas.height = size;

    // Draw rectangles with different colors
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        const color = colors[i][j]
        if (!color) {
          continue
        }
        ctx.fillStyle = color;
        ctx.fillRect(i, j, 1, 1);
      }
    }

    // Get base64 representation
    return canvas.toDataURL();
  }


  showHelp() {
    console.log("ewewew")
    this.dialog.open(HelpDialogComponent, {
      autoFocus: false, // Prevents dialog from auto-closing on click inside
    });
  }
}
