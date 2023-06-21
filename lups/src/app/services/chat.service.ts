import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {Observable} from "rxjs";


export interface ChatResponse {
  output_text_en: string;
  output_text_ee: string;
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private url = 'api/chat'; // Replace with your server endpoint

  constructor(private http: HttpClient) { }

  sendChatMessage(text: string): Observable<ChatResponse> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { text: text };
    // return this.http.get<ChatResponse>(this.url, { headers: headers })
    return this.http.post<ChatResponse>(this.url, body, { headers: headers });
  }
}
