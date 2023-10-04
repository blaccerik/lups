import {Injectable} from '@angular/core';
import {Socket} from 'ngx-socket-io';
import {Observable, Observer} from "rxjs";
import {OAuthService} from "angular-oauth2-oidc";
import {HttpClient} from "@angular/common/http";


export interface PixelResponse {
  x: number,
  y: number,
  c: number,
  color: string
}

@Injectable({
  providedIn: 'root'
})
export class PlaceService {

  constructor(private socket: Socket,
              private http: HttpClient,
              private oauthService: OAuthService) {}

  sendData(x: number, y: number, color: string) {
    const data = {
      x: x,
      y: y,
      color: color
    }
    this.socket.emit("update", data)
  }

  // Method to listen to a custom event from the server
  receiveMyResponse(): Observable<PixelResponse> {
    return this.socket.fromEvent('update_response');
  }

  // Connect to the WebSocket server
  connect(): Observable<string> {
    return new Observable((observer) => {
      // Create the extraHeaders object
      const extraHeaders: { [key: string]: string } = {};
      if (this.oauthService.hasValidIdToken()) {
        const accessToken = this.oauthService.getIdToken();
        extraHeaders['Authorization'] = `Bearer ${accessToken}`;
      }
      const socketOptions = {
        url: this.socket.ioSocket.io.uri,
        options: {
          extraHeaders: extraHeaders  // Assign the extraHeaders object
        }
      };
      // Disconnect from the previous socket, if any
      console.log(this.socket.ioSocket.io.uri);
      this.socket.disconnect();
      this.socket = new Socket(socketOptions);
      this.socket.on('connect', () => {
        console.log('Connected to the server.');
        observer.next('Socket connection successful'); // Emit a success value
        observer.complete(); // Complete the observable
      });

      this.socket.on('connect_error', (error: any) => {
        console.error('Socket connection error:', error);
        observer.error('Socket connection error'); // Emit an error value
      });
    });
  }

  getPixels(): Observable<PixelResponse[]> {
    return this.http.get<PixelResponse[]>("api/place")
  }

  // Disconnect from the WebSocket server
  disconnect() {
    this.socket.disconnect();
  }
}
