import {computed, effect, inject, Injectable, OnDestroy, Signal, signal} from '@angular/core';
import {map, Observable, Subscription} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {OAuthService} from "angular-oauth2-oidc";
import {Message} from "../components/chat/chat.component";
import {toSignal} from "@angular/core/rxjs-interop";
import {ActivatedRoute, Params} from "@angular/router";

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

export interface ChatMessage {
  id: number
  text: string
  owner: string
  language: string
}

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private url = 'api/chat';
  private http = inject(HttpClient)

  language = signal('english')
  model = signal("small")
  chats = signal([] as ChatData[])

  constructor() {
    this.http.get<ChatData[]>(this.url + "/").subscribe(data => {
      this.chats.set(data)
    })
  }


  // chatId = signal(0)
  // private chats$ =  this.http.get<ChatData[]>(this.url + "/")
  // chats: Signal<ChatData[]> = toSignal(this.chats$, {initialValue: []});
  //
  // test = computed(() => {
  //   return this.chats()
  // })


  getChatMessages(id: number): Observable<ChatMessage[]> {
    return this.http.get<ChatMessage[]>(this.url + "/" + id)
  }

  editChatTitle(id: number, title: string): Observable<any> {
    const data = {
      title: title
    }
    return this.http.put<any>(this.url + "/" + id, data)
  }

    postMessage(id: number, chatSend: ChatMessage): Observable<ChatSendRespond> {
    return this.http.post<ChatSendRespond>(this.url + "/" + id, chatSend)
  }

  getStreamMessages(streamId: string): Observable<ChatReceive> {
    const eventSource = new EventSource(this.url + "/stream/" + streamId)
    return new Observable<ChatReceive>((observer) => {

      eventSource.onmessage = (m) => {
        const chatReceive = JSON.parse(m.data)
        observer.next(chatReceive)
        if (chatReceive.type === "end") {
          eventSource.close()
          observer.complete()
        }
      }

      eventSource.onerror = (e) => {
        console.log(e)
        eventSource.close()
        observer.complete()
      }

      // // need to use event listener or else zone js isn't triggered
      // eventSource.addEventListener("message", m => {
      //   const chatReceive = JSON.parse(m.data)
      //   observer.next(chatReceive)
      //   if (chatReceive.type === "end") {
      //     eventSource.close()
      //     observer.complete()
      //   }
      // })
      // eventSource.addEventListener("error", e => {
      //   console.log(e)
      //   eventSource.close()
      //   observer.complete()
      // })
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
