import {
  AfterViewChecked,
  Component,
  effect,
  ElementRef,
  inject,
  OnDestroy,
  OnInit,
  signal,
  ViewChild
} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {ChatData, ChatReceive, ChatSend, ChatService} from "../../services/chat.service";
import {ActivatedRoute, Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../../services/user-info.service";
import {BreakpointObserver} from "@angular/cdk/layout";
import {Subscription} from "rxjs";
import {ChatBoxComponent} from "./chat-box/chat-box.component";
import {ChatDrawerComponent} from "./chat-drawer/chat-drawer.component";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";

export interface Message {
  message_id: number
  message_text: string
  message_owner: string
}

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    ChatBoxComponent,
    ChatDrawerComponent,
    MatDrawer,
    MatDrawerContent,
    MatDrawerContainer,
    MatIcon,
    MatIconButton
  ],
  templateUrl: './chat.component.html',
  styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
  private route = inject(ActivatedRoute)
  private chatService = inject(ChatService)
  drawerOpen = signal(false)
  chatId = signal(0)
  chats = signal<ChatData[]>([])


  textField: string;
  messages: Message[];
  // chatId: number;
  // chats: ChatData[]
  streamId: string;
  messagesLoaded: boolean;
  form: FormGroup;
  private streamSubscription: Subscription;

  languages = [
    // {display: 'Eesti', value: 'estonia'},
    {display: 'Inglise', value: 'english'},
  ];
  models = [
    {display: 'Väike', value: 'small'},
    // {display: 'Suur', value: 'large'},
  ];

  constructor(
              private router: Router,
              private oauthService: OAuthService,
              public userInfoService: UserInfoService,
              private observer: BreakpointObserver,
              private fb: FormBuilder
  ) {
    //   const chats = this.chats()
    //   console.log("effect", chats)
    //   if (chats.length) {
    //     this.router.navigate(['/chat', chats[0].chat_id]);
    //   }
    // });
    // this.form = this.fb.group({
    //   language: ['english', Validators.required],
    //   model: ['small', Validators.required],

  }


  isStreaming = false;


  hasLoaded(): boolean {
    return this.messagesLoaded
  }

  ngOnDestroy() {
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe()
    }
  }

  ngOnInit() {
    // load all user chats
    this.chatService.getChats().subscribe(
      chats => {
        // this.chatService.chats.set(chats)
        // listen to url changes
        this.route.params.subscribe(params => {
          const chatId = params["id"]
          if (!chatId) {
            const lastChat = chats[chats.length - 1]
            console.log("new", lastChat.chat_id)
            // this.chatId.set(lastChat.chat_id)
            this.chatService.chatId.set(lastChat.chat_id)
            this.router.navigate(['/chat', lastChat.chat_id]);
          } else {
            this.chatService.chatId.set(chatId)
          }
        })
      }
    )


    //   next: (chats: ChatData[]) => {
    //     this.chats = chats

    // // listen to url changes
    // this.route.params.subscribe(params => {
    //   console.log("params", params["id"])
    //   // no chat id
    //   // this.chatId.set(params["id"])
    //
    //   // const chatId = params["id"]
    //   // console.log(chatId)
    //   // if (!chatId) {
    //   //   const lastChat = this.chats[this.chats.length - 1]
    //     this.router.navigate(['/chat', 1]);
    //   // } else {
    //   //   // this.loadComponent(chatId)
    //   // }
    // })
    // }
    // })


  }

  loadComponent(id: number) {
    console.log("compobnent load", id)
    // this.chatId = id
    this.messagesLoaded = false
    this.messages = []
    this.textField = ""
    this.streamId = ""
    this.isStreaming = false;

    // unsub if needed
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe()
    }

    // get all messages in a chat
    // this.getAllMessagesInChat()
  }

  // private getAllMessagesInChat(): void {
  //   this.chatService.getMessages(this.chatId).subscribe({
  //     next: (messages: Message[]) => {
  //       console.log(messages)
  //       this.messages = messages;
  //       this.messagesLoaded = true;
  //     },
  //     error: err => {
  //       console.log(err)
  //       // this.router.navigate([""])
  //     }
  //   })
  // }

  ngAfterViewChecked() {
    this.scrollToBottom();
  }

  @ViewChild('scrollContainer') private scrollContainer: ElementRef | undefined;

  scrollToBottom(): void {
    const container = this.scrollContainer?.nativeElement
    if (!container) {
      return
    }
    container.scrollTo({
      top: container.scrollHeight,
      behavior: 'smooth' // Add smooth scroll behavior
    });
  }

  private updateUserMessageId(id: number): void {
    // find last user message without id
    const msg = this.messages.find(o => o.message_owner === "user" && o.message_id === -1)
    if (msg) {
      msg.message_id = id
    }
  }

  private updateModelMessage(chatReceive: ChatReceive): void {
    this.messages[this.messages.length - 1].message_text = chatReceive.text

    // need to use for loop or else the ui is messed up
    let msg: Message | null = null
    for (let i = this.messages.length - 1; i >= 0; i--) {
      const message = this.messages[i]
      if (message.message_id === -1 && message.message_owner === "model") {
        msg = message
        break
      }
    }
    if (!msg) {
      msg = {
        message_id: chatReceive.id,
        message_text: chatReceive.text,
        message_owner: "model"
      }
      this.messages.push(msg)
    }
    if (chatReceive.type === "part") {
      msg.message_text = chatReceive.text
    } else if (chatReceive.type === "end") {
      msg.message_text = chatReceive.text
      msg.message_id = chatReceive.id
      this.isStreaming = false;
    }
  }


  send() {
    this.isStreaming = true;
    const message: ChatSend = {
      type: "message",
      ai_model_type: this.form.value["model"],
      language_type: this.form.value["language"],
      message_id: -1,
      message_text: this.textField,
    }
    this.messages.push({
      message_id: -1,
      message_owner: "user",
      message_text: this.textField
    })
    this.messages.push({
      message_id: -1,
      message_owner: "model",
      message_text: "Loading..."
    })

    // this.chatService.postMessage(this.chatId, message).subscribe({
    //   next: chatSendRespond => {
    //     console.log("stream id", chatSendRespond)
    //     this.streamId = chatSendRespond.stream_id
    //     this.updateUserMessageId(chatSendRespond.message_id)
    //     this.streamSubscription = this.chatService.getStreamMessages(this.streamId).subscribe({
    //       next: chatReceive => {
    //         this.updateModelMessage(chatReceive)
    //       }
    //     })
    //   }
    // })
    this.textField = ""
  }

  cancel() {
    this.chatService.deleteStream(this.streamId).subscribe(
      () => {
        this.streamId = ""
      }
    )
  }

  createNew() {
    this.messagesLoaded = false
    this.chatService.newChat().subscribe({
      next: (chatData: ChatData) => {
        // this.chats.push(chatData)
        this.router.navigate(["chat", chatData.chat_id])
      }
    })
  }


}
