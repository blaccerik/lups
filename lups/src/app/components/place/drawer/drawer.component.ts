import {Component, ElementRef, EventEmitter, OnInit, Output, ViewChild} from '@angular/core';


export interface Color {
  value: string
  text: string
}

export interface Tool {
  selectedTool: string | null
  brushColor: Color
  brushSize: number
  imgSize: number
  originalImage: string | null
  editedImage: string | null
  imageColors: string[]
}

@Component({
  selector: 'app-drawer',
  templateUrl: './drawer.component.html',
  styleUrls: ['./drawer.component.scss']
})
export class DrawerComponent implements OnInit {

  colors: Color[] = [
    {value: 'red', text: "punane"},
    {value: 'green', text: "roheline"},
    {value: 'blue', text: "sinine"},
    {value: 'yellow', text: "kollane"},
    {value: 'purple', text: "lilla"},
    {value: 'orange', text: "oranž"},
    {value: 'black', text: "must"},
    {value: 'white', text: "valge"},
  ];

  shadows: boolean
  names: boolean
  tool: Tool

  @Output() dataEvent = new EventEmitter<Tool>();

  listOfColors: number[][] = [
    [255, 0, 0],
    [150, 33, 77],
    [75, 99, 23],
    [45, 88, 250],
    [250, 0, 255]
  ];

  ngOnInit(): void {
    // set default values
    this.tool = {
      selectedTool: null,
      brushColor: this.colors[0],
      brushSize: 1,
      imgSize: 10,
      originalImage: null,
      editedImage: null,
      imageColors: []
    }
  }


  @ViewChild('canvas', {static: true}) canvasRef: ElementRef;
  private context: CanvasRenderingContext2D | null;

  private drawColors() {
    const a = this.canvasRef
    console.log(a)
    // this.context = (this.canvasRef.nativeElement as HTMLCanvasElement).getContext('2d');
    //
    // console.log(this.context)
    // const canvas = this.colorCanvas.nativeElement;
    // const ctx = canvas.getContext('2d');
    // if (!ctx) {
    //   return
    // }
    //
    // console.log(ctx)
    // const pixelSize = 20; // Adjust this size based on your preference
    //
    // canvas.width = this.listOfColors.length * pixelSize;
    // canvas.height = pixelSize;
    //
    // this.listOfColors.forEach((color, index) => {
    //   ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
    //   ctx.fillRect(index * pixelSize, 0, pixelSize, pixelSize);
    // });
  }

  selectTool(tool: string) {
    if (this.tool.selectedTool === tool) {
      this.tool.selectedTool = null
    } else {
      this.tool.selectedTool = tool
    }
    this.dataEvent.emit(this.tool)
  }

  increaseBrushSize() {
    if (this.tool.brushSize < 4) {
      this.tool.brushSize++
    }
    this.dataEvent.emit(this.tool)
  }

  decreaseBrushSize() {
    if (this.tool.brushSize > 1) {
      this.tool.brushSize--
    }
    this.dataEvent.emit(this.tool)
  }

  selectColor(color: Color) {
    this.tool.brushColor = color
    this.dataEvent.emit(this.tool)
  }

  increaseImageSize() {
    if (this.tool.imgSize < 19) {
      this.tool.imgSize++
    }

    if (!this.tool.originalImage) {
      return
    }
    const image = new Image();
    image.src = this.tool.originalImage
    image.onload = () => {

      // update edited image
      const rgbArray = this.compressImage(image)
      const newRGBArray = this.mapValuesToColors(rgbArray)
      this.tool.editedImage = this.createImage(newRGBArray)
      this.dataEvent.emit(this.tool)
    };
  }

  decreaseImageSize() {
    if (this.tool.imgSize > 11) {
      this.tool.imgSize--
    }


    if (!this.tool.originalImage) {
      return
    }
    const image = new Image();
    image.src = this.tool.originalImage
    image.onload = () => {

      // update edited image
      const rgbArray = this.compressImage(image)
      const newRGBArray = this.mapValuesToColors(rgbArray)
      this.tool.editedImage = this.createImage(newRGBArray)
      this.dataEvent.emit(this.tool)
    };
  }

  changeShadows() {
  }

  changeNames() {

  }

  @ViewChild('fileInput', {static: false}) fileInput: ElementRef;

  clearImage(event: Event) {
    event.stopPropagation();
    this.tool.originalImage = null
    this.tool.editedImage = null
    this.tool.imageColors = []
    this.selectedImage = null

    // Reset the value of the file input without triggering a click event
    this.fileInput.nativeElement.value = '';
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

      const image = new Image();

      image.onload = () => {

        // update edited image
        const rgbArray = this.compressImage(image)
        const newRGBArray = this.mapValuesToColors(rgbArray)
        this.tool.editedImage = this.createImage(newRGBArray)
      };

      image.src = this.selectedImage;
    };
    reader.readAsDataURL(file);
  }

  compressImage(img: HTMLImageElement) {
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
    const rgbArray: number[][] = [];

    // Iterate through the pixel data array and extract RGB values
    for (let i = 0; i < pixelData.length; i += 4) {
      const red = pixelData[i];
      const green = pixelData[i + 1];
      const blue = pixelData[i + 2];

      // Add RGB values to the array
      rgbArray.push([red, green, blue]);
    }
    return rgbArray
  }


  closestColor(listOfColors: number[][], targetColor: number[]): number[] {
    const colors = listOfColors.map(color => this.calculateDistance(color, targetColor));
    return listOfColors[colors.indexOf(Math.min(...colors))];
  }

  private calculateDistance(color1: number[], color2: number[]): number {
    const squaredDifferences = color1.map((value, index) => (value - color2[index]) ** 2);
    const sumSquaredDifferences = squaredDifferences.reduce((acc, val) => acc + val, 0);
    return Math.sqrt(sumSquaredDifferences);
  }

  mapValuesToColors(values: number[][]): number[][] {
    const listOfColors = [
      [255, 0, 0],       // Red
      [0, 255, 0],       // Green
      [0, 0, 255],       // Blue
      [255, 255, 0],     // Yellow
      // [0, 255, 255],     // Cyan
      [255, 0, 255],     // Magenta
      [0, 0, 0],         // Black
      [255, 255, 255],   // White
      // [128, 128, 128],   // Gray
      // [165, 42, 42],     // Brown
      [255, 165, 0],     // Orange
      // [128, 0, 128],     // Purple
      // [255, 182, 193],   // Pink
      // [0, 128, 128],     // Teal
      // [230, 230, 250],   // Lavender
      // [128, 128, 0]      // Olive
    ]
    // return values
    return values.map(value => this.closestColor(listOfColors, value))
  }

  createImage(values: number[][]) {
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
        const color = values[i + j * size]
        ctx.fillStyle = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
        ctx.fillRect(i, j, 1, 1);
      }
    }

    // Get base64 representation
    return canvas.toDataURL();
  }

}
