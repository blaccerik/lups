import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {map, Observable} from "rxjs";
import {Message} from "../chat/chat.component";


export interface ChatResponse {
  id: number,
  message: string,
  type: string
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private url = 'api/chat'; // Replace with your server endpoint

  constructor(private http: HttpClient) { }

  get(id: number): Observable<Message[]> {
    return this.http.get<ChatResponse[]>(this.url + "/" + id).pipe(
      map((chatResponses: ChatResponse[]) => {
        return chatResponses.map((c: ChatResponse) => {
          const m: Message = {
            id: c.id,
            message: c.message,
            isLoading: false,
            isUser: c.type === "user"
          };
          return m;
        });
      })
    );
  }

  chats(): Observable<number[]> {
    return this.http.get<number[]>(this.url)
  }

  delete(id: number): Observable<string> {
    return this.http.delete<string>(this.url + "/" + id)
  }

  create(text: string, id: number): Observable<string> {
    return this.http.post<string>(this.url + "/create", null)
  }

  send(text: string, id: number): Observable<ChatResponse> {
    const body = { text: text };
    return this.http.post<ChatResponse>(this.url + "/" + id, body)
  }

  // sendChatMessage(text: string): Observable<ChatResponse> {
  //   const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
  //   const body = { text: text };
  //   // return this.http.get<ChatResponse>(this.url, { headers: headers })
  //   return this.http.post<ChatResponse>(this.url, body, { headers: headers });
  // }
}
