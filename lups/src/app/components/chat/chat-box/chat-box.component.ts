import {Component, effect, inject, OnDestroy, signal} from '@angular/core';
import {ActivatedRoute} from "@angular/router";
import {ChatMessage, ChatService} from "../../../services/chat.service";
import {merge, of, Subscription, switchMap, throwIfEmpty} from "rxjs";
import {NgForOf, NgIf} from "@angular/common";
import {FormBuilder, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatInput} from "@angular/material/input";
import {MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {toSignal} from "@angular/core/rxjs-interop";
import {dateTimestampProvider} from "rxjs/internal/scheduler/dateTimestampProvider";

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
  private streamId$: Subscription | null = null
  private stream$: Subscription | null = null
  messages = signal<ChatMessage[] | null>(null)
  isWaiting = signal(false)
  chatId = signal(-1)
  streamId = signal("")

  constructor() {

    effect(() => {
      const streamId = this.streamId()

      // console.log(this.streamId())
    })

    this.messages$ = this.activatedRoute.params.pipe(
      switchMap(params => {
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
    })
  }

  ngOnDestroy(): void {
    if (this.messages$) {
      this.messages$.unsubscribe()
    }
    if (this.stream$) {
      this.stream$.unsubscribe()
    }
    if (this.streamId$) {
      this.streamId$.unsubscribe()
    }
  }

  send() {
    const text = this.form.value.text
    if (text && !this.isWaiting()) {
      this.isWaiting.set(true)
      const userMessage: ChatMessage = {
        text: text,
        language: this.chatService.language(),
        owner: "user",
        id: -1
      }
      const modelMessage: ChatMessage = {
        text: "loading...",
        language: this.chatService.language(),
        owner: this.chatService.model(),
        id: -1
      }
      const messages = this.messages()
      if (messages) {
        this.messages.set([...messages, userMessage, modelMessage])
      }
      this.streamId$ = this.chatService.postMessage(this.chatId(), userMessage).subscribe(
        data => {
          this.streamId.set(data.stream_id)
          const messages = this.messages()
          if (!messages) {
            return
          }
          const last = messages.find(m => m.owner === "user" && m.id === -1)
          if (last) {
            last.id = data.message_id
          }
          this.messages.set([...messages])

          // todo does not update on html
          // when using effect + console log then it does :(
          // use effect with streamid to update messages maybe?
          this.stream$ = this.chatService.getStreamMessages(data.stream_id).subscribe(
            textPart => {
              // find last bot message
              const messages = this.messages()
              if (!messages) {
                return
              }
              const m = messages.find(m => m.owner !== "user" && m.id === -1)
              if (!m) {
                return;
              }
              m.text = textPart.text
              if (textPart.type === "end") {
                m.id = textPart.id
                this.isWaiting.set(false)
              }
              // this.messages.set([{
              //   owner: "2",
              //   text: "wewe",
              //   language: "ee",
              //   id: -1
              // }])
              // this.messages.update(
              //   messages => {
              //     if (!messages) {
              //       return messages
              //     }
              //     const m = messages.find(m => m.owner !== "user" && m.id === -1)
              //     if (!m) {
              //       return messages
              //     }
              //     m.text = textPart.text
              //     console.log(m)
              //     // msgs?.find()
              //     return [{
              //       owner: "2",
              //       text: "wewe",
              //       language: "ee",
              //       id: -1
              //     }]
              //   }
              // )
              this.messages.set([...messages])
              // console.log(textPart)
              // console.log(messages)
            }
          )

        }
      )
    }
    this.form.reset()
  }

  new() {
    console.log("neew")
  }
}
