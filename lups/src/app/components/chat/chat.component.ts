import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import {ChatReceive, ChatSend, ChatService} from "../../services/chat.service";
import {Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../../services/user-info.service";
import {MatSidenav} from "@angular/material/sidenav";
import {BreakpointObserver} from "@angular/cdk/layout";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";

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
export class ChatComponent implements OnInit {
  textField = "";
  messages: Message[] = [];
  id = -1;
  messagesLoaded = false;
  websocketLoaded = false
  form: FormGroup;

  languages = [
    { display: 'Eesti', value: 'estonia' },
    { display: 'Inglise', value: 'english' },
  ];
  models = [
    { display: 'Väike', value: 'small' },
    { display: 'Suur', value: 'large' },
  ];

  constructor(private chatService: ChatService,
              private router: Router,
              private oauthService: OAuthService,
              public userInfoService: UserInfoService,
              private observer: BreakpointObserver,
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

  toggleSidenav() {
    this.isSidenavOpen = !this.isSidenavOpen;
  }

  hasLoaded(): boolean {
    return this.websocketLoaded && this.messagesLoaded
  }

  ngOnInit() {

    if (!this.oauthService.hasValidIdToken()) {
      localStorage.setItem('originalUrl', window.location.pathname);
      this.oauthService.initLoginFlow('google');
      return
    }

    // get all chats
    this.chatService.getChats().subscribe({
      next: (chats: number[]) => {
        this.id = chats[0]

        // connect to websocket
        this.connectToWebsocket()

        // get all messages in a chat
        this.getAllMessagesInChat()
      },
      error: err => {
        console.log(err)
        // this.router.navigate([""])
      }
    })
  }

  getAllMessagesInChat(): void {
    this.chatService.getMessages(this.id).subscribe({
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

  connectToWebsocket(): void {
    this.chatService.connect(this.id).subscribe({
      next: (chatReceive: ChatReceive) => {
        switch (chatReceive.type) {
          case "data":
            this.receiveDataType(chatReceive)
            break
          case "stream_message":
          case "message":
            this.receiveMessageType(chatReceive)
            break
          case "error":
            this.receiveErrorType(chatReceive)
            break
          case "completed":
            this.receiveCompletedType(chatReceive)
            break
          default:
            console.log(chatReceive)
            console.log("unknown type")
        }
      },

    })
  }

  receiveCompletedType(chatReceive: ChatReceive) {
    console.log("completed", chatReceive.message_text)
    this.websocketLoaded = true
  }

  receiveErrorType(chatReceive: ChatReceive) {
    console.log("error", chatReceive.message_text)
  }

  receiveDataType(chatReceive: ChatReceive) {
    console.log("data", chatReceive.queue_number)
  }

  receiveMessageType(chatReceive: ChatReceive) {
    if (chatReceive.type == "message") {
      this.messages.push({
        message_id: chatReceive.message_id,
        message_text: chatReceive.message_text,
        message_owner: chatReceive.message_owner
      })
      return
    }

    // find last message
    const reversedMessages = [...this.messages].reverse();
    let modelMessage = reversedMessages.find(message => message.message_owner === "model");
    if (!modelMessage) {
      modelMessage = {
        message_id: chatReceive.message_id,
        message_text: chatReceive.message_text,
        message_owner: chatReceive.message_owner
      }
      this.messages.push(modelMessage)
    }
    modelMessage.message_text = chatReceive.message_text
  }

  send() {
    // const message: ChatSend = {
    //   type: "message",
    //   ai_model_type: this.model,
    //   language_type: this.language,
    //   message_id: -1,
    //   message_text: this.textField,
    // }
    // this.messages.push({
    //   message_id: -1,
    //   message_owner: "user",
    //   message_text: this.textField
    // })
    // this.messages.push({
    //   message_id: -1,
    //   message_owner: "model",
    //   message_text: "Loading..."
    // })
    // this.chatService.send(message)
    this.textField = ""
  }
  //
  // cancel() {
  //   const message: ChatSend = {
  //     type: "cancel",
  //     ai_model_type: this.model,
  //     language_type: this.language,
  //     message_id: -1,
  //     message_text: "",
  //   }
  //   this.chatService.send(message)
  // }
  //
  // clear() {
  //   const message: ChatSend = {
  //     type: "delete",
  //     ai_model_type: this.model,
  //     language_type: this.language,
  //     message_id: -1,
  //     message_text: "",
  //   }
  //   this.chatService.send(message)
  //   this.messages = []
  //   this.hasLoaded = false
  // }

}
