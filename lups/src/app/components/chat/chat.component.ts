import {Component, ElementRef, NgZone, ViewChild} from '@angular/core';
import {ChatResponse, ChatService} from "../../services/chat.service";
import {Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../../services/user-info.service";
import {HttpClient, HttpDownloadProgressEvent, HttpEvent, HttpEventType} from "@angular/common/http";

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
              public userInfoService: UserInfoService
  ) {

    if (!this.oauthService.hasValidIdToken()) {
      this.oauthService.initLoginFlow('google');
    }
    this.id = -1;
    this.chatService.chats().subscribe({
      next: (chats: number[]) => {
        console.log(chats)
        this.id = chats[0]
        this.chatService.get(this.id).subscribe({
          next: (msgs: Message[]) => {
            this.messages = msgs;
            this.hasLoaded = true;
            // Scroll to the latest question
            setTimeout(() => {
              this.scrollToBottom();
            }, 0);
          },
          error: err => {
            console.log(err)
            this.router.navigate([""])
          }
        })
      },
      error: err => {
        console.log(err)
        this.router.navigate([""])
      }
    })
    // stream chat
    // this.chatService.stream().subscribe({
    //   next: (event: HttpEvent<string>) => {
    //     if (event.type === HttpEventType.DownloadProgress) {
    //       this.someChat = (event as HttpDownloadProgressEvent).partialText!
    //     } else if (event.type === HttpEventType.Response) {
    //       this.someChat = event.body!
    //     }
    //   },
    //   error: err => {
    //     this.someChat = ""
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

  scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } catch (err) {
      console.log(err);
    }
  }
}
