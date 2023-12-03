import {Injectable} from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable, retry, Subject} from "rxjs";
import {Message} from "../components/chat/chat.component";
import {OAuthService} from "angular-oauth2-oidc";
import {environment} from "../../environments/environment";
import {webSocket} from "rxjs/webSocket";


export interface ChatReceive {
  type: string
  // data
  queue_number: number
  // message
  message_id: number
  message_text: string
  message_owner: string
}

export interface ChatSend {
  type: string
  ai_model_type: string
  language_type: string
  message_text: string
  message_id: number
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private url = 'api/chat';
  private subject: any;
  private messagesSubject = new Subject<ChatReceive>();

  constructor(private http: HttpClient, private oauthService: OAuthService) {
    if (!this.oauthService.hasValidIdToken()) {
      return
    }
  }

  connect(chat_id: number): Observable<ChatReceive> {
    const token = this.oauthService.getIdToken();
    console.log("ws url", environment.wsUrl)
    this.subject = webSocket(`${environment.wsUrl}/api/chat/${chat_id}?authorization=${token}`);
    // get websocket
    this.subject.pipe(retry({delay: 3000})).subscribe((chatReceive: ChatReceive) => {
      this.messagesSubject.next(chatReceive)
    })
    return this.messagesSubject.asObservable();
  }

  getMessages(id: number): Observable<Message[]> {
    return this.http.get<Message[]>(this.url + "/" + id)
  }

  getChats(): Observable<number[]> {
    return this.http.get<number[]>(this.url + "/")
  }

  send(chatSend: ChatSend): void {
    this.subject.next(chatSend)
  }
}
