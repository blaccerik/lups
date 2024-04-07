import {Component, effect, inject, signal} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {ChatData, ChatService} from "../../services/chat.service";
import {ActivatedRoute, Params, Router} from "@angular/router";
import {ChatBoxComponent} from "./chat-box/chat-box.component";
import {ChatDrawerComponent} from "./chat-drawer/chat-drawer.component";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";
import {toSignal} from "@angular/core/rxjs-interop";

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
export class ChatComponent {
  private activatedRoute = inject(ActivatedRoute)
  private chatService = inject(ChatService)
  private router = inject(Router)
  chats = signal<ChatData[]>([])
  route$ = this.activatedRoute.params
  route = toSignal(this.route$, {initialValue: {} as Params})

  constructor() {
    // navigate to chat with id if chat id is not given
    effect(() => {
      const chats = this.chatService.chats()
      const route = this.route()
      const chatId = route["id"]
      if (!chatId && chats.length > 0) {
        const lastChat = chats[chats.length - 1]
        this.router.navigate(['/chat', lastChat.chat_id]);
      }
    })
  }


}
