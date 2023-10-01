import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import {Observable} from "rxjs";
import {OAuthService} from "angular-oauth2-oidc";
import {HttpClient} from "@angular/common/http";
import {NewsResponse} from "./news.service";


export interface PixelResponse {
  x: number,
  y: number,
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
  connect(): Observable<PixelResponse[]> {
    // Create the extraHeaders object
    const extraHeaders: { [key: string]: string } = {};

    if (this.oauthService.hasValidIdToken()) {
      const accessToken = this.oauthService.getIdToken();
      extraHeaders['Authorization'] = `Bearer ${accessToken}`

    }

    // Create the socketOptions with the updated extraHeaders
    const socketOptions = {
      url: this.socket.ioSocket.io.uri,  // Use the same URL as the existing socket
      options: {
        extraHeaders: extraHeaders  // Assign the extraHeaders object
      }
    };
    console.log(this.socket.ioSocket.io.uri)
    this.socket.disconnect(); // Disconnect from the previous socket, if any
    this.socket = new Socket(socketOptions);

    return this.http.get<PixelResponse[]>("api/place")
  }

  // Disconnect from the WebSocket server
  disconnect() {
    this.socket.disconnect();
  }
}
