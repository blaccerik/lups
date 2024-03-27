import {Component, effect, inject, OnDestroy, signal} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {ChatMessage, ChatService} from "../../../services/chat.service";
import {merge, of, Subscription, switchMap} from "rxjs";
import {NgForOf} from "@angular/common";

@Component({
  selector: 'app-chat-box',
  standalone: true,
  imports: [
    NgForOf
  ],
  templateUrl: './chat-box.component.html',
  styleUrl: './chat-box.component.scss'
})
export class ChatBoxComponent implements OnDestroy {
  private chatService = inject(ChatService)
  private activatedRoute = inject(ActivatedRoute)

  messages = signal<ChatMessage[] | null>(null)
  messages$: Subscription

  constructor() {
    this.messages$ = this.activatedRoute.params.pipe(
      switchMap(params => {
        const id = params["id"]
        if (!id) {
          return of(null)
        }
        return merge(
          of(null), // Emit null initially
          this.chatService.getChatMessages(params["id"])
        );
      })
    ).subscribe(data => {
      this.messages.set(data)
    })
  }

  ngOnDestroy(): void {
    if (this.messages$) {
      this.messages$.unsubscribe()
    }
  }
}
