import {Component, OnDestroy, OnInit} from '@angular/core';
import {ChatReceive, ChatSend, ChatService} from "../../services/chat.service";
import {ActivatedRoute, Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../../services/user-info.service";
import {BreakpointObserver} from "@angular/cdk/layout";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {Subscription} from "rxjs";

export interface Message {
  message_id: number
  message_text: string
  message_owner: string
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent implements OnInit, OnDestroy {
  textField: string;
  messages: Message[];
  chatId: number;
  streamId: string;
  messagesLoaded: boolean;
  form: FormGroup;
  private streamSubscription: Subscription;

  languages = [
    {display: 'Eesti', value: 'estonia'},
    {display: 'Inglise', value: 'english'},
  ];
  models = [
    {display: 'Väike', value: 'small'},
    {display: 'Suur', value: 'large'},
  ];

  constructor(private chatService: ChatService,
              private router: Router,
              private oauthService: OAuthService,
              public userInfoService: UserInfoService,
              private observer: BreakpointObserver,
              private route: ActivatedRoute,
              private fb: FormBuilder
  ) {
    this.form = this.fb.group({
      language: ['english', Validators.required],
      model: ['small', Validators.required],
    });
  }

  onSubmit() {
    if (this.form.valid) {
      // Do something with the form data
      console.log(this.form.value);
    } else {
      // Handle invalid form
      console.log('Form is invalid');
    }
  }

  isSidenavOpen = false;
  isStreaming = false;

  toggleSidenav() {
    this.isSidenavOpen = !this.isSidenavOpen;
  }

  hasLoaded(): boolean {
    return this.messagesLoaded
  }

  ngOnDestroy() {
    if (this.streamSubscription) {
      this.streamSubscription.unsubscribe()
    }
  }

  ngOnInit() {
    if (!this.oauthService.hasValidIdToken()) {
      localStorage.setItem('originalUrl', window.location.pathname);
      this.oauthService.initLoginFlow('google');
      return
    }

    this.route.params.subscribe(params => {
      console.log("params", params)
      // no chat id
      const chatId = params["id"]
      if (!chatId) {
        this.chatService.getChats().subscribe({
          next: (chats: number[]) => {
            console.log("chats", chats)
            const lastChat = chats[chats.length - 1]
            this.router.navigate(['/chat', lastChat]);
            // this.loadComponent(lastChat)
          }
        })
      } else {
        this.loadComponent(chatId)
      }
    })
  }

  loadComponent(id: number) {
    console.log("compobnent load", id)
    this.chatId = id
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
    this.getAllMessagesInChat()
  }

  private getAllMessagesInChat(): void {
    this.chatService.getMessages(this.chatId).subscribe({
      next: (messages: Message[]) => {
        console.log(messages)
        this.messages = messages;
        this.messagesLoaded = true;
        // // Scroll to the latest question
        // setTimeout(() => {
        //   this.scrollToBottom();
        // }, 0);
      },
      error: err => {
        console.log(err)
        // this.router.navigate([""])
      }
    })
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

    this.chatService.postMessage(this.chatId, message).subscribe({
      next: chatSendRespond => {
        console.log("stream id", chatSendRespond)
        this.streamId = chatSendRespond.stream_id
        this.updateUserMessageId(chatSendRespond.message_id)
        this.streamSubscription = this.chatService.getStreamMessages(this.streamId).subscribe({
          next: chatReceive => {
            this.updateModelMessage(chatReceive)
          }
        })
      }
    })
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
      next: (chatId: number) => {
        this.router.navigate(["chat", chatId])
      }
    })
  }
}
