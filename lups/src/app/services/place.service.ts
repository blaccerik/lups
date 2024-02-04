import {Injectable} from '@angular/core';
import {map, Observable, retry, Subject} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {OAuthService} from "angular-oauth2-oidc";
import {environment} from "../../environments/environment";
import {webSocket} from "rxjs/webSocket";
import {Tool} from "../components/place/drawer/drawer.component";

export interface PixelResponse {
  x: number,
  y: number,
  color: string
  user: string
}

interface PixelResponseCompressed {
  x: number,
  y: number,
  c: string,
  u: string
}


@Injectable({
  providedIn: 'root'
})
export class PlaceService {

  private subject: any;
  private messagesSubject = new Subject<PixelResponse[]>();
  predefinedColors = [
    "red", "green", "blue", "yellow", "purple", "orange", "black", "white"
  ];

  constructor(private http: HttpClient, private oauthService: OAuthService) {

    let token = ""
    if (this.oauthService.hasValidIdToken()) {
      token = this.oauthService.getIdToken();
    }
    console.log(environment.wsUrl)
    this.subject = webSocket(`${environment.wsUrl}/api/place/ws?authorization=${token}`);

    // get websocket
    this.subject.pipe(retry({delay: 1000})).subscribe((pixelInputs: PixelResponseCompressed[]) => {
      // Map the compressed data to PixelResponse format
      this.messagesSubject.next(pixelInputs.map((compressed: PixelResponseCompressed) => {
        return {
          x: compressed.x,
          y: compressed.y,
          color: compressed.c,
          user: compressed.u
        };
      }));
    })
  }

  getPixels(): Observable<PixelResponse[]> {
    return this.http.get<PixelResponseCompressed[]>("api/place/").pipe(
      map(data => {
        // Transform the data here
        return data.map((pixelInput: PixelResponseCompressed) => {
          return {
            user: pixelInput.u,
            color: pixelInput.c,
            x: pixelInput.x,
            y: pixelInput.y
          };
        });
      })
    );
  }

  connect(): any {
    return this.messagesSubject.asObservable();
  }

  disconnect() {
    if (this.subject) {
      this.subject.unsubscribe()
    }
  }

  send(x: number, y: number, tool: Tool) {
    let matrix: (string | null)[][]
    let size: number
    if (tool.selectedTool === "brush") {
      matrix = tool.brushMatrix
      size = tool.brushSize
    } else if (tool.selectedTool === "image") {
      matrix = tool.imageMatrix
      size = tool.imgSize
    } else {
      throw Error("Tool not selected")
    }
    this.subject.next({
      tool: tool.selectedTool,
      x: x,
      y: y,
      size: size,
      matrix: matrix
    })
  }
}
