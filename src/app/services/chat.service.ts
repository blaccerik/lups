import { Injectable } from '@angular/core';
import {map, Observable} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {OAuthService} from "angular-oauth2-oidc";
import {Message} from "../components/chat/chat.component";

export interface ChatReceive {
  type: string
  id: number
  text: string
}

export interface ChatSend {
  type: string
  ai_model_type: string
  language_type: string
  message_text: string
  message_id: number
}

export interface ChatSendRespond {
  stream_id: string
  message_id: number
}

export interface ChatData {
  title: string
  chat_id: number
  editing: boolean
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private url = 'api/chat';

  constructor(private http: HttpClient, private oauthService: OAuthService) {}

  getMessages(id: number): Observable<Message[]> {
    return this.http.get<Message[]>(this.url + "/" + id)
  }

  editChatTitle(id: number, title: string): Observable<any> {
    const data = {
      title: title
    }
    return this.http.put<any>(this.url + "/" + id, data)
  }

  postMessage(id: number, chatSend: ChatSend): Observable<ChatSendRespond> {
    return this.http.post<ChatSendRespond>(this.url + "/" + id, chatSend)
  }

  getStreamMessages(streamId: string): Observable<ChatReceive> {
    const eventSource = new EventSource(this.url + "/stream/" + streamId)
    return new Observable<ChatReceive>((observer) => {
      // need to use event listener or else zone js isn't triggered
      eventSource.addEventListener("message", m => {
        const chatReceive = JSON.parse(m.data)
        observer.next(chatReceive)
        if (chatReceive.type === "end") {
          eventSource.close()
          observer.complete()
        }
      })
      eventSource.addEventListener("error", e => {
        console.log(e)
        eventSource.close()
        observer.complete()
      })
    })
  }

  deleteStream(streamId: string): Observable<any> {
    return this.http.delete<any>(this.url + "/stream/" + streamId)
  }

  getChats(): Observable<ChatData[]> {
    return this.http.get<ChatData[]>(this.url + "/")
  }

  newChat(): Observable<ChatData> {
    return this.http.get<ChatData>(this.url + "/new").pipe(
        map(c => {
          c.editing = false
          return c
        })
    )
  }
}
