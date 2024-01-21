import {PixelResponse, PlaceService} from "../../services/place.service";
import {
  ChangeDetectorRef,
  Component,
  ElementRef,
  HostListener,
  OnDestroy,
  OnInit,
  Renderer2,
  ViewChild
} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {PopupService} from "../../services/popup.service";
import {MatDialog} from "@angular/material/dialog";
import {HelpDialogComponent} from "./help-dialog/help-dialog.component";
import {Subscription} from "rxjs";

interface Color {
  value: string
  text: string
}

interface Tool {
  icon: string
  time: Date
  text: string
  value: string
}

@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.scss']
})
export class PlaceComponent implements OnInit, OnDestroy {

  selectedOption: string;

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
  tools: Tool[] = [
    {icon: "brush", text: "pliiats", time: new Date(), value: "brush"},
    {icon: "image", text: "pilt", time: new Date(), value: "image"}
  ]
  selectedC: Color


  selectOption(option: Color): void {
    this.selectedC = option
  }

  predefinedColors = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
  ];
  selectedTool: string | null
  brushColor: string
  brushSize: number
  imgSize: number
  img: string[]

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

  @ViewChild('canvasContainer', {static: false}) containerRef: ElementRef<HTMLDivElement>;
  @ViewChild('canvasElement', {static: false}) canvasElement: ElementRef<HTMLCanvasElement>;

  @HostListener('document:mouseup', ['$event'])
  onMouseUpGlobal(event: MouseEvent): void {
    this.isDragging = false;
  }

  @HostListener('window:resize', ['$event'])
  onWindowResize(event: Event) {
    if (this.canvas) {
      this.findOffset(this.offsetX, this.offsetY)
    }
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


  constructor(
    private placeService: PlaceService,
    private readonly authService: OAuthService,
    public readonly popupService: PopupService,
    private dialog: MatDialog,
    private cdRef: ChangeDetectorRef,
    private renderer: Renderer2) {
  }


  private placeService$: Subscription
  isSideDrawerOpen = false

  toggleDrawer() {
    this.isSideDrawerOpen = !this.isSideDrawerOpen
  }

  selectTool(tool: string) {
    if (this.selectedTool === tool) {
      this.selectedTool = null
    } else {
      this.selectedTool = tool;
    }
  }

  ngOnInit(): void {
    // set default values
    this.selectedTool = null
    this.brushColor = this.colors[0].value
    this.brushSize = 1
    this.imgSize = 3
    this.img = []



    this.selectedC = this.colors[0]
    this.placeService$ = this.placeService.getPixels().subscribe({
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

        // connect to websocket
        this.placeService.connect().subscribe(
          (pixelResponse: PixelResponse) => {
            this.context.fillStyle = pixelResponse.color
            this.context.fillRect(pixelResponse.x * this.pixelSize, pixelResponse.y * this.pixelSize, this.pixelSize, this.pixelSize);
          }
        );
      }
    })
  }

  ngOnDestroy() {
    if (this.placeService$) {
      this.placeService$.unsubscribe()
    }
    this.placeService.disconnect()
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
    this.context.fillStyle = "red"
    this.context.fillRect(x * this.pixelSize, y * this.pixelSize, this.pixelSize, this.pixelSize);
    this.context.fillStyle = "grey"
    this.context.fillRect(x * this.pixelSize, y * this.pixelSize, 1, 1);
    this.context.fillRect(x * this.pixelSize + 3, y * this.pixelSize, 1, 1);
    this.context.fillRect(x * this.pixelSize, y * this.pixelSize + 3, 1, 1);
    this.context.fillRect(x * this.pixelSize + 3, y * this.pixelSize + 3, 1, 1);

    // send request to backend
    this.placeService.send(x, y, "red")
  }

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }

  showHelp() {
    this.dialog.open(HelpDialogComponent, {
      autoFocus: false, // Prevents dialog from auto-closing on click inside
    });
  }
}


