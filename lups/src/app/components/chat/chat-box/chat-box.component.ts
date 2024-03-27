import {Component, effect, inject, OnDestroy, signal} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {ChatMessage, ChatService} from "../../../services/chat.service";
import {merge, of, Subscription, switchMap} from "rxjs";
import {NgForOf, NgIf} from "@angular/common";
import {FormBuilder, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatInput} from "@angular/material/input";
import {MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {MatProgressSpinner} from "@angular/material/progress-spinner";

@Component({
  selector: 'app-chat-box',
  standalone: true,
  imports: [
    NgForOf,
    ReactiveFormsModule,
    MatFormField,
    FormsModule,
    MatLabel,
    MatIcon,
    MatInput,
    MatIconButton,
    NgIf,
    MatMiniFabButton,
    MatProgressSpinner
  ],
  templateUrl: './chat-box.component.html',
  styleUrl: './chat-box.component.scss'
})
export class ChatBoxComponent implements OnDestroy {
  private chatService = inject(ChatService)
  private activatedRoute = inject(ActivatedRoute)
  private fb = inject(FormBuilder)
  form = this.fb.group({
    text: ["", Validators.required],
  });

  private readonly messages$: Subscription | null = null
  messages = signal<ChatMessage[] | null>(null)

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
