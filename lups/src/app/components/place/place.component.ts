import {PixelResponse, PlaceService} from "../../services/place.service";
import {Component, HostListener, ViewChild, ElementRef, Renderer2, OnInit} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {PopupService} from "../../services/popup.service";
import {MatDialog} from "@angular/material/dialog";
import {HelpDialogComponent} from "../../services/help-dialog/help-dialog.component";


@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.scss']
})
export class PlaceComponent {

  selectedColor: string = 'white';
  predefinedColors: string[] = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
  ];
  @ViewChild('canvas', {static: false}) set content(content: ElementRef) {
    if (content) {
      this.canvas = content;
      this.context = this.canvas.nativeElement.getContext('2d');
      for (let i = 0; i < this.data.length; i++) {
        const response = this.data[i]
        this.context.fillStyle = response.color
        this.context.fillRect(response.x * this.pixelSize, response.y * this.pixelSize, this.pixelSize, this.pixelSize);
      }
      this.receiveEventFromServer();
    }
  }
  private data: PixelResponse[] = []
  private context: CanvasRenderingContext2D;
  private canvas: ElementRef;

  private pixelSize = 4; // Size of each pixel
  canvasWidth = 300 * this.pixelSize;
  canvasHeight = 300 * this.pixelSize;
  private lastPixelPlacementTimestamp = 0;
  loading = true;

  canPlacePixel(): boolean {
    const currentTime = Date.now();
    if (currentTime - this.lastPixelPlacementTimestamp >= 1000) {
      this.lastPixelPlacementTimestamp = currentTime;
      return true;
    } else {
      return false;
    }
  }

  placePixel(event: MouseEvent): void {
    event.preventDefault(); // Prevent the default context menu

    if (!this.context) return;

    if (!this.authService.hasValidIdToken()) {
      this.popupService.addPopup("You are not logged in");
      return;
    }

    if (!this.canPlacePixel()) {
      this.popupService.addPopup("Placing too fast");
      return;
    }

    const x = Math.floor(event.offsetX / this.pixelSize);
    const y = Math.floor(event.offsetY / this.pixelSize);

    // send request to backend
    this.placeService.sendData(x, y, this.selectedColor)
  }

  @ViewChild('container') containerRef!: ElementRef;

  private isDragging = false;
  private startX = 0;
  private startY = 0;
  private minScale = 1.0;
  private maxScale = 4.0;
  scale = 2;
  offsetX = 0;
  offsetY = 0;

  onMouseDown(event: MouseEvent): void {
    // console.log(event)
    this.isDragging = true;
    this.startX = event.clientX - this.offsetX;
    this.startY = event.clientY - this.offsetY;
    this.renderer.addClass(this.canvas.nativeElement, 'dragging');

  }

  @HostListener('document:mouseup', ['$event'])
  onMouseUpGlobal(event: MouseEvent): void {
    this.isDragging = false;
  }

  @HostListener('window:resize', ['$event'])
  onWindowResize(event: Event) {
    this.findOffset(this.offsetX, this.offsetY)
  }

  onMouseMove(event: MouseEvent): void {
    if (!this.isDragging) return;
    const newX = event.clientX - this.startX;
    const newY = event.clientY - this.startY;
    console.log(event.clientX, this.offsetX)
    this.findOffset(newX, newY)
  }

  private findOffset(newX: number, newY: number): void {
    const image = this.canvas.nativeElement as HTMLDivElement
    const container = this.containerRef.nativeElement;

    const result1 = image.offsetWidth + (image.offsetWidth / 2 * (this.scale - 1));
    const blockx1 = -(result1 - container.offsetWidth)
    const blockx2 = result1 - image.offsetWidth

    const result2 = image.offsetHeight + (image.offsetHeight / 2 * (this.scale - 1));
    const blocky1 = -(result2 - container.offsetHeight)
    const blocky2 = result2 - image.offsetHeight

    this.offsetX = Math.min(Math.max(newX, blockx1), blockx2)
    this.offsetY = Math.min(Math.max(newY, blocky1), blocky2)
    // console.log(this.offsetY)
    // console.log(this.offsetY, "=", blocky2, newY, blocky1, "|", image.offsetHeight, container.offsetHeight)
  }

  onWheel(event: WheelEvent): void {
    event.preventDefault();
    console.log(this.offsetX)
    if (event.deltaY < 0) {
      this.scale = Math.min(this.maxScale, this.scale + 0.1);
    } else {
      this.scale = Math.max(this.minScale, this.scale - 0.1);
    }
    this.findOffset(this.offsetX, this.offsetY)
    console.log(this.offsetX)
  }

  onMouseUp(event: MouseEvent): void {
    this.isDragging = false;
  }

  constructor(
    private placeService: PlaceService,
    private readonly authService: OAuthService,
    public readonly popupService: PopupService,
    private dialog: MatDialog,
    private renderer: Renderer2) { }

  ngOnInit(): void {
    this.selectedColor = "white"
  }

  ngAfterViewInit(): void {
    for (let i = 0; i < 300; i++) {
      for (let j = 0; j < 300; j++) {
        let color = "white"
        if ((i + j) % 10 === 0) {
          color = "red"
        }
        if ((i + 2 * j) % 60 === 0) {
          color = "green"
        }
        this.data.push({
          color: color,
          x: i,
          y: j,
        })
      }
    }
    for (let i = 0; i < 300; i++) {
      this.data.push({
        color: "black",
        x: i,
        y: 10

      })

      this.data.push({
        color: "black",
        x: 10,
        y: i

      })

      this.data.push({
        color: "purple",
        x: 290,
        y: i

      })

      this.data.push({
        color: "blue",
        x: 150,
        y: i

      })
    }
    this.loading = false
    // this.placeService.connect().subscribe({ next: (data: PixelResponse[]) => {
    //     this.loading = false;
    //     this.data = data;
    //   }});
  }

  selectColor(color: string): void {
    this.selectedColor = color;
  }

  // Method to receive events from the server
  receiveEventFromServer() {
    // this.placeService.receiveMyResponse().subscribe((response: PixelResponse) => {
    //   this.context.fillStyle = response.color
    //   this.context.fillRect(response.x * this.pixelSize, response.y * this.pixelSize, this.pixelSize, this.pixelSize);
    // });
  }

  isMenuOpen = false;

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  showHelp() {

    this.dialog.open(HelpDialogComponent);


    // this.dialog.open(HelpDialogComponent, {
    //   width: "400px",
    //   hasBackdrop: true,
    //   closeOnNavigation: true
    // });
  }
}


