import {Injectable} from '@angular/core';
import {map, Observable, retry, Subject} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {OAuthService} from "angular-oauth2-oidc";
import {environment} from "../../environments/environment";
import {webSocket} from "rxjs/webSocket";

export interface PixelResponse {
  x: number,
  y: number,
  color: string
}

@Injectable({
  providedIn: 'root'
})
export class PlaceService {

  private subject: any;
  private messagesSubject = new Subject<PixelResponse>();
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
    this.subject.pipe(retry({delay: 1000})).subscribe((message: any) => {
      this.messagesSubject.next({
        color: message.color,
        x: message.x,
        y: message.y
      })
    })
  }

  getPixels(): Observable<PixelResponse[]> {
    return this.http.get<any>("api/place/").pipe(
      map(data => {
        // Transform the data here
        return data.map((message: any) => {
          return {
            color: this.predefinedColors[message.c],
            x: message.x,
            y: message.y
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

  send(x: number, y: number, color: string) {
    this.subject.next({
      x: x,
      y: y,
      color: color
    })
  }
}
