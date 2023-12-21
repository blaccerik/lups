import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable, retry, Subject} from "rxjs";
import {Message} from "../components/chat/chat.component";
import {OAuthService} from "angular-oauth2-oidc";
import {environment} from "../../environments/environment";
import {webSocket, WebSocketSubject} from "rxjs/webSocket";


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

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private url = 'api/chat';
  // private subject: WebSocketSubject<any>;
  // private messagesSubject: Subject<ChatReceive>

  constructor(private http: HttpClient, private oauthService: OAuthService) {
    if (!this.oauthService.hasValidIdToken()) {
      return
    }
  }

  getMessages(id: number): Observable<Message[]> {
    return this.http.get<Message[]>(this.url + "/" + id)
  }

  postMessage(id: number, chatSend: ChatSend): Observable<ChatSendRespond> {
    return this.http.post<ChatSendRespond>(this.url + "/" + id, chatSend)
  }

  getStreamMessages(streamId: string): Observable<ChatReceive> {
    const eventSource = new EventSource(this.url + "/stream/" + streamId)
    return new Observable<ChatReceive>((observer) => {
      eventSource.onmessage = (event: MessageEvent<any>) => {
        const chatReceive = JSON.parse(event.data)
        observer.next(chatReceive)
        if (chatReceive.type === "end") {
          eventSource.close()
          observer.complete()
        }
      };
      eventSource.onerror = (error: Event) => {
        console.log(error)
        eventSource.close()
        observer.complete()
      };
    })
  }

  deleteStream(streamId: string): Observable<any> {
    return this.http.delete<any>(this.url + "/stream/" + streamId)
  }

  getChats(): Observable<number[]> {
    console.log("chats")
    return this.http.get<number[]>(this.url + "/")
  }

  newChat(): Observable<number> {
    return this.http.get<number>(this.url + "/new")
  }

  // send(chatSend: ChatSend): void {
  //   this.subject.next(chatSend)
  // }
}
