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
import {Subscription} from "rxjs";
import {Tool} from "./drawer/drawer.component";

interface Block {
  color: string,
  user?: string,
}

interface OverlayBlock {
  x: number,
  y: number
}

@Component({
  selector: 'app-place',
  templateUrl: './place.component.html',
  styleUrls: ['./place.component.scss']
})
export class PlaceComponent implements OnInit, OnDestroy {

  private context: CanvasRenderingContext2D;
  private canvas: HTMLCanvasElement
  private container: HTMLDivElement
  private pixelSize = 4; // Size of each pixel
  private lastPixelPlacementTimestamp = 0;
  loading = true;
  private isDragging = false;
  private startX = 0;
  private startY = 0;
  private minScale = 1.0;
  private maxScale = 4.0;
  scale = 1;
  offsetX = 0;
  offsetY = 0;
  isMouseOnCanvas: boolean = false;
  private blocks: Block[][]
  private overlayBlocks: OverlayBlock[]
  private placeService$: Subscription
  isSideDrawerOpen = false
  tool: Tool

  @ViewChild('canvasContainer', {static: false}) containerRef: ElementRef<HTMLDivElement>;
  @ViewChild('canvasElement', {static: false}) canvasElement: ElementRef<HTMLCanvasElement>;
  @ViewChild('canvasTooltip') canvasTooltip: ElementRef<HTMLDivElement>;

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

  onMouseEnterCanvas(): void {
    this.isMouseOnCanvas = true;
  }

  onMouseLeaveCanvas(): void {
    this.clearOverlay()
    this.isMouseOnCanvas = false;
  }

  private addToOverlayBlocks(x: number, y: number) {
    if (0 <= x && x < 300 && 0 <= y && y < 300) {
      this.overlayBlocks.push({
        x: x,
        y: y
      })
    }
  }

  private addToBlocks(x: number, y: number, block: Block) {
    if (0 <= x && x < 300 && 0 <= y && y < 300) {
      this.blocks[x][y] = block
    }
  }

  private clearOverlay() {

    if (!this.context) return;

    for (const overlayBlock of this.overlayBlocks) {
      this.context.fillStyle = this.blocks[overlayBlock.x][overlayBlock.y].color
      this.context.fillRect(
        overlayBlock.x * this.pixelSize,
        overlayBlock.y * this.pixelSize,
        this.pixelSize,
        this.pixelSize
      );
    }
    this.overlayBlocks = []
  }

  private drawOverlayToCanvas(
    x: number,
    y: number,
    size: number,
    matrix: (string | null)[][],
    temp: boolean
  ) {
    if (!this.context) return;

    // check if mismatch, it happens rarely
    if (size !== matrix.length) return;

    const delta = Math.floor(size / 2)
    for (let i = 0; i < size; i++) {
      for (let j = 0; j < size; j++) {
        const color = matrix[i][j]
        if (!color) {
          continue;
        }

        this.context.fillStyle = color
        const dx = x + i - delta
        const dy = y + j - delta
        if (temp) {
          this.addToBlocks(dx, dy, {
            color: color
          })
        } else {
          this.addToOverlayBlocks(dx, dy)
        }
        this.context.fillRect(
          dx * this.pixelSize,
          dy * this.pixelSize,
          this.pixelSize,
          this.pixelSize
        )
      }
    }
  }

  private drawOverlay(x: number, y: number) {

    // check if can draw overlay
    if (!this.tool.shadows) return;

    if (this.tool.selectedTool === "brush") {
      this.drawOverlayToCanvas(x, y, this.tool.brushSize, this.tool.brushMatrix, false)
    } else if (this.tool.selectedTool === "image" && this.tool.originalImage) {
      this.drawOverlayToCanvas(x, y, this.tool.imgSize, this.tool.imageMatrix, false)
    }
  }

  onMouseMove(event: MouseEvent): void {

    // find mouse coords
    const rect = this.containerRef.nativeElement.getBoundingClientRect()
    const scaledMouseX = event.clientX - rect.x; // - canvasRect.left;
    const scaledMouseY = event.clientY - rect.y;  //- canvasRect.top;

    // Position the tooltip next to the mouse
    if (this.canvasTooltip) {
      this.canvasTooltip.nativeElement.style.left = scaledMouseX + 25 + 'px';
      this.canvasTooltip.nativeElement.style.top = scaledMouseY + 'px';
    }

    // draw overlay
    if (!this.isDragging) {

      const x = Math.floor(event.offsetX / this.pixelSize);
      const y = Math.floor(event.offsetY / this.pixelSize);

      // clean prev overlay
      this.clearOverlay()

      this.drawOverlay(x, y)
      return
    }

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


  receiveData(data: Tool) {
    this.tool = data;
  }

  ngOnInit(): void {

    // set default values
    this.tool = {
      selectedTool: null,
      brushColor: {value: 'red', text: "punane", rgb: [255, 0, 0]},
      brushSize: 1,
      imgSize: 10,
      originalImage: null,
      editedImage: null,
      imageMatrix: [],
      brushMatrix: [["red"]],
      shadows: false,
      names: false
    }

    // init map
    const size = 300
    this.blocks = new Array(size)
    for (let i = 0; i < size; i++) {
      this.blocks[i] = new Array(size)
      for (let j = 0; j < size; j++) {
        this.blocks[i][j] = {
          color: "white"
        }
      }
    }
    this.overlayBlocks = []

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
          // update map
          this.blocks[pixelResponse.x][pixelResponse.y] = {
            color: pixelResponse.color,
            user: "erik"
          }

          // draw on canvas
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

    if (!this.tool.selectedTool) {
      this.popupService.addPopup("Tool not selected");
      return;
    }

    if (this.tool.selectedTool === "image" && !this.tool.originalImage) {
      this.popupService.addPopup("Image not selected");
      return;
    }

    if (!this.canPlacePixel()) {
      this.popupService.addPopup("Placing too fast");
      return;
    }

    const x = Math.floor(event.offsetX / this.pixelSize);
    const y = Math.floor(event.offsetY / this.pixelSize);

    // place dummy pixels until backend responds
    if (this.tool.selectedTool === "image" && this.tool.originalImage) {
      this.drawOverlayToCanvas(x, y, this.tool.imgSize, this.tool.imageMatrix, true)
    } else if (this.tool.selectedTool === "brush") {
      this.drawOverlayToCanvas(x, y, this.tool.brushSize, this.tool.brushMatrix, true)
    }

    // send request to backend
    this.placeService.send(x, y, this.tool)
  }
}


