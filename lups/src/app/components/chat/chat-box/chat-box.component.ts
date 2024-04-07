import {AfterViewChecked, Component, effect, ElementRef, inject, OnDestroy, signal, ViewChild} from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
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
export class ChatBoxComponent implements OnDestroy, AfterViewChecked {
  private chatService = inject(ChatService)
  private activatedRoute = inject(ActivatedRoute)
  private router = inject(Router)
  private fb = inject(FormBuilder)
  form = this.fb.group({
    text: ["", Validators.required],
  });

  private readonly messages$: Subscription | null = null
  private streamId$: Subscription | null = null
  private stream$: Subscription | null = null
  messages = signal<ChatMessage[] | null>(null)
  isWaiting = signal(false)
  chatId = signal(-1)
  streamId = signal("")

  constructor() {
    // only purpose of the effect is to tell angular messages has been updated
    // otherwise if chat stream parts come in then html wont be updated :/
    effect(() => {
      this.messages()
    });

    this.messages$ = this.activatedRoute.params.pipe(
      switchMap(params => {
        this.messages.set(null)
        this.chatId.set(-1)
        this.streamId.set("")
        this.isWaiting.set(false)
        const id = params["id"]
        if (!id) {
          return of(null)
        } else {
          this.chatId.set(id)
        }
        return merge(
          of(null), // Emit null initially
          this.chatService.getChatMessages(params["id"])
        );
      })
    ).subscribe(data => {
      this.messages.set(data)
      // use timeout so dom can update from signal
      setTimeout(() => {
        this.scrollToBottom()
      }, 0)
    })
  }

  private unsub() {
    if (this.stream$) {
      this.stream$.unsubscribe()
    }
    if (this.streamId$) {
      this.streamId$.unsubscribe()
    }
  }

  ngOnDestroy(): void {
    if (this.messages$) {
      this.messages$.unsubscribe()
    }
    this.unsub()
  }

  send() {
    const text = this.form.value.text
    this.form.reset()
    if (!text || this.isWaiting()) {
      return
    }
    this.isWaiting.set(true)
    const userMessage: ChatMessage = {
      text: text,
      language: this.chatService.language(),
      owner: "user",
      id: -1
    }
    const modelMessage: ChatMessage = {
      text: "Loading...",
      language: this.chatService.language(),
      owner: this.chatService.model(),
      id: -1
    }

    // update messages
    const messages = this.messages()
    if (messages) {
      this.messages.set([...messages, userMessage, modelMessage])
    }
    setTimeout(() => {
      this.scrollToBottom()
    }, 0)

    // send post request
    const sendMessage: ChatMessage = {
      text: userMessage.text,
      id: -1,
      owner: modelMessage.owner,
      language: modelMessage.language
    }
    this.streamId$ = this.chatService.postMessage(this.chatId(), sendMessage).subscribe(
      data => {
        this.streamId.set(data.stream_id)
        const messages = this.messages()
        if (!messages) {
          return
        }

        const userMessage = messages.find(message => message.owner === "user" && message.id === -1)
        if (userMessage) {
          userMessage.id = data.message_id
        }
        this.messages.set([...messages])

        // start listening for chat stream
        this.stream$ = this.chatService.getStreamMessages(data.stream_id).subscribe(
          textPart => {
            const messages = this.messages()
            if (!messages) {
              return
            }

            // find last bot message
            const botMessage = messages.find(message => message.owner !== "user" && message.id === -1)
            if (botMessage) {
              botMessage.text = textPart.text
              if (textPart.type === "end") {
                botMessage.id = textPart.id

                // reset values
                this.isWaiting.set(false)
                this.streamId.set("")
              }
            }
            this.messages.set([...messages])
          }
        )
      }
    )
  }

  cancel() {
    const streamId = this.streamId()
    if (!streamId) {
      return
    }
    this.form.reset()
    this.chatService.deleteStream(streamId).subscribe()
  }

  new() {
    this.chatService.newChat().subscribe(
      data => {
        this.chatService.chats.set([...this.chatService.chats(), data])
        this.messages.set(null)
        this.streamId.set("")
        this.isWaiting.set(true)
        this.chatId.set(-1)
        this.unsub()
        this.router.navigate(["chat", data.chat_id])
      }
    )
  }


  ngAfterViewChecked() {
    // this.scrollToBottom();
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
}
