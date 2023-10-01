import {PixelResponse, PlaceService} from "../../services/place.service";
import {
  Component,
  HostListener,
  ViewChild,
  ElementRef,
  Renderer2,
  OnInit,
  AfterViewInit,
  ChangeDetectorRef
} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {PopupService} from "../../services/popup.service";
import {MatDialog} from "@angular/material/dialog";
import {HelpDialogComponent} from "./help-dialog/help-dialog.component";


@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.scss']
})
export class PlaceComponent implements OnInit {

  selectedColor: string = 'white';
  predefinedColors: string[] = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
  ];
  private context: CanvasRenderingContext2D;
  private canvas: HTMLCanvasElement
  private container: HTMLDivElement
  private pixelSize = 4; // Size of each pixel
  private lastPixelPlacementTimestamp = 0;
  loading = true;
  isMenuOpen = false;
  private isDragging = false;
  private startX = 0;
  private startY = 0;
  private minScale = 1.0;
  private maxScale = 4.0;
  scale = 1;
  offsetX = 0;
  offsetY = 0;

  @ViewChild('canvasContainer', { static: false }) containerRef: ElementRef<HTMLDivElement>;
  @ViewChild('canvasElement', { static: false }) canvasElement: ElementRef<HTMLCanvasElement>;

  @HostListener('document:mouseup', ['$event'])
  onMouseUpGlobal(event: MouseEvent): void {
    this.isDragging = false;
  }

  @HostListener('window:resize', ['$event'])
  onWindowResize(event: Event) {
    this.findOffset(this.offsetX, this.offsetY)
  }

  onMouseDown(event: MouseEvent): void {
    // console.log(event)
    this.isDragging = true;
    this.startX = event.clientX - this.offsetX;
    this.startY = event.clientY - this.offsetY;
    this.renderer.addClass(this.canvas, 'dragging');

  }

  onMouseMove(event: MouseEvent): void {
    if (!this.isDragging) return;
    const newX = event.clientX - this.startX;
    const newY = event.clientY - this.startY;
    this.findOffset(newX, newY)
  }

  onWheel(event: WheelEvent): void {
    event.preventDefault();
    const oldScale = this.scale
    if (event.deltaY < 0) {
      this.scale = Math.min(this.maxScale, this.scale + 0.5);
    } else {
      this.scale = Math.max(this.minScale, this.scale - 0.5);
    }

    // find new offsets
    const x = this.offsetX + (this.canvas.offsetWidth / 2 - event.offsetX) * (this.scale - oldScale)
    const y = this.offsetY + (this.canvas.offsetWidth / 2 - event.offsetY) * (this.scale - oldScale)
    this.findOffset(x, y);
  }

  onMouseUp(event: MouseEvent): void {
    this.isDragging = false;
  }

  constructor(
    private placeService: PlaceService,
    private readonly authService: OAuthService,
    public readonly popupService: PopupService,
    private dialog: MatDialog,
    private cdRef: ChangeDetectorRef,
    private renderer: Renderer2) { }

  ngOnInit(): void {
    this.placeService.connect().subscribe({
    next: (value: PixelResponse[]) => {
      this.loading = false;
      // setup objects
      this.cdRef.detectChanges(); // Trigger change detection
      const canvas = this.canvasElement.nativeElement;
      const container = this.containerRef.nativeElement
      const context = canvas.getContext('2d');
      if (!context) {
        return
      }
      this.container = container
      this.canvas = canvas
      this.context = context

      // draw canvas
      for (const pixelResponse of value) {
        this.context.fillStyle = pixelResponse.color
        this.context.fillRect(pixelResponse.x * this.pixelSize, pixelResponse.y * this.pixelSize, this.pixelSize, this.pixelSize);
      }
    }})

    this.placeService.receiveMyResponse().subscribe((response: PixelResponse) => {
      this.context.fillStyle = response.color
      this.context.fillRect(response.x * this.pixelSize, response.y * this.pixelSize, this.pixelSize, this.pixelSize);
    });
  }

  private loadCanvas(): void {
    this.context.fillStyle = 'white';
    this.context.fillRect(0, 0, this.canvas.width, this.canvas.height);

    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;
    const squareSize = 100;

    this.context.fillStyle = 'blue';
    this.context.fillRect(centerX - squareSize / 2, centerY - squareSize / 2, squareSize, squareSize);

    this.context.fillStyle = "black"
    this.context.fillRect(0, 10, 1200, 2)
    this.context.fillRect(10, 0, 2, 1200)
    this.context.fillRect(0, 1190, 1200, 2)
    this.context.fillRect(1190, 0, 2, 1200)
    this.context.fillRect(1100, 0, 2, 1200)
    for (let i = 0; i < 60; i++) {
      this.context.fillStyle = "blue"
      this.context.fillRect(i * 20, 0, 2, 1200)
    }
    this.context.fillStyle = "red"
    this.context.fillRect(420, 0, 2, 1200)
    this.context.fillStyle = "green"
    this.context.fillRect(440, 0, 2, 1200)

    this.context.fillStyle = "orange"
    this.context.fillRect(600, 0, 2, 1200)

    this.context.fillStyle = "orange"
    this.context.fillRect(800, 0, 2, 1200)
  }

  selectColor(color: string): void {
    this.selectedColor = color;
  }

  private findOffset(newX: number, newY: number): void {
    const image = this.canvas
    const container = this.container;

    const result1 = image.offsetWidth + (image.offsetWidth / 2 * (this.scale - 1));
    const blockx1 = -(result1 - container.offsetWidth)
    const blockx2 = result1 - image.offsetWidth

    const result2 = image.offsetHeight + (image.offsetHeight / 2 * (this.scale - 1));
    const blocky1 = -(result2 - container.offsetHeight)
    const blocky2 = result2 - image.offsetHeight

    this.offsetX = Math.min(Math.max(newX, blockx1), blockx2)
    this.offsetY = Math.min(Math.max(newY, blocky1), blocky2)
  }

  private canPlacePixel(): boolean {
    const currentTime = Date.now();
    if (currentTime - this.lastPixelPlacementTimestamp >= 500) {
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

    // place dummy pixel until backend responds
    this.context.fillStyle = this.selectedColor
    this.context.fillRect(x * this.pixelSize, y * this.pixelSize, this.pixelSize, this.pixelSize);
    this.context.fillStyle = "grey"
    this.context.fillRect(x * this.pixelSize, y * this.pixelSize, 1, 1);
    this.context.fillRect(x * this.pixelSize + 3, y * this.pixelSize, 1, 1);
    this.context.fillRect(x * this.pixelSize, y * this.pixelSize + 3, 1, 1);
    this.context.fillRect(x * this.pixelSize + 3, y * this.pixelSize + 3, 1, 1);

    // send request to backend
    this.placeService.sendData(x, y, this.selectedColor)
  }

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  showHelp() {
    this.dialog.open(HelpDialogComponent);
  }
}


