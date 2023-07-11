import {Component, ElementRef, NgZone, ViewChild} from '@angular/core';
import {ChatResponse, ChatService} from "../../services/chat.service";
import {Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../../services/user-info.service";
import {HttpClient, HttpDownloadProgressEvent, HttpEvent, HttpEventType} from "@angular/common/http";
import {SseClient} from 'ngx-sse-client';

export interface Message {
  id: number,
  message: string,
  isUser: boolean,
  isLoading: boolean
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent {

  @ViewChild('chatContainer') private chatContainer: ElementRef;


  textField: string = "";
  messages: Message[] = [];
  id: number = -1;
  hasLoaded: boolean = false;
  someChat: string = "e"
  constructor(private chatService: ChatService,
              private router: Router,
              private oauthService: OAuthService,
              public userInfoService: UserInfoService,
              private zone: NgZone,
              private http: HttpClient,
              private sseClient: SseClient
  ) {

    this.http.get('api/chat/stream', {
      responseType: 'text',
      observe: 'events',
      reportProgress: true,
    }).subscribe({
    next: (event: HttpEvent<string>) => {
      if (event.type === HttpEventType.DownloadProgress) {
        this.someChat = (event as HttpDownloadProgressEvent).partialText!
      } else if (event.type === HttpEventType.Response) {
        this.someChat = event.body!
      }
    }, error: (err) => {
      console.log(err)
    }});

    // this.sseClient.stream('api/chat/stream', { responseType: 'text' }).subscribe({
    //   next: value => {
    //     console.log(value)
    //   }
    // })


    // let o = new Observable<string>(obs => {
    //   const es = new EventSource('api/chat/stream');
    //   es.addEventListener('message', (evt) => {
    //     console.log(evt.data);
    //     obs.next(evt.data);
    //   });
    //   return () => es.close();
    // });
    //
    // o.subscribe(m => {
    //   console.log(m)
    // })

    // this.http.get('api/chat/stream', {
    //   responseType: "text/event-stream"
    // })
    //   .subscribe( { next: m => {
    //       console.log(m)
    //     },
    //     error: err => {
    //       console.log(err)
    //     }
    //   });
    // this.eventSource = new SSE('api/chat/stream', options);
    // this.eventSource = new EventSource('api/chat/stream');
    // // Process default event
    //
    // this.zone.run(() => {
    //   this.eventSource.onmessage = (event: MessageEvent) => {
    //     console.log(event)
    //   }
    // })

  }



  send() {

    const userMessage: Message = {
      id: -1,
      message: this.textField,
      isUser: true,
      isLoading: false
    };
    this.messages.push(userMessage);

    const appMessage: Message = {
      id: -1,
      message: "loading...",
      isUser: false,
      isLoading: true
    };
    this.messages.push(appMessage);

    this.chatService.send(this.textField, this.id).subscribe({
      next: (response: ChatResponse) => {
        console.log(response.message)
        const msg: Message = {
          id: response.id,
          message: response.message,
          isUser: false,
          isLoading: false
        };
        const loadingMessageIndex = this.messages.findIndex(msg => msg.isLoading);
        if (loadingMessageIndex > -1) {
          this.messages.splice(loadingMessageIndex, 1);
        }
        this.messages.push(msg)
      },
      error: err => {
        console.log(err)
        this.router.navigate([""])
      }
    })
    this.textField = ""
    // Scroll to the latest question
    setTimeout(() => {
      this.scrollToBottom();
    }, 0);
  }

  clear() {
    this.hasLoaded = false
    this.chatService.delete(this.id).subscribe({
      next: (r: string) => {
        this.messages = []
        this.hasLoaded = true
      },
      error: err => {
        console.log(err)
        this.router.navigate([""])
      }
    })
  }



  // submit() {
  //   const userMessage: Message = {
  //     text: this.textFieldValue,
  //     isUser: true,
  //     isLoading: false
  //   };
  //   this.messages.push(userMessage);
  //
  //   const loadingMessage: Message = {
  //     text: "",
  //     isUser: false,
  //     isLoading: true
  //   };
  //   this.messages.push(loadingMessage);
  //
  //   this.sendPostRequest(this.textFieldValue);
  //   this.textFieldValue = ""; // Clear the input field
  //
  //   // Scroll to the latest question
  //   setTimeout(() => {
  //     this.scrollToBottom();
  //   }, 0);
  // }
  //
  // sendPostRequest(msg: string) {
  //   this.chatService.sendChatMessage(msg).subscribe({
  //     next: (response: ChatResponse) => {
  //       const loadingMessageIndex = this.messages.findIndex(msg => msg.isLoading);
  //       if (loadingMessageIndex > -1) {
  //         this.messages.splice(loadingMessageIndex, 1);
  //       }
  //
  //       const appMessage: Message = {
  //         text: response.output_text_ee,
  //         isUser: false,
  //         isLoading: false
  //       };
  //       this.messages.push(appMessage);
  //
  //     },
  //     error: (error: any) => {
  //       console.log(error);
  //     }
  //   });
  // }
  //
  scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } catch (err) {
      console.log(err);
    }
  }
}
