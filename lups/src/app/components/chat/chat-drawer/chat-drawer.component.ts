import {Component, effect, inject, Input, input, OnInit, signal} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatIcon} from "@angular/material/icon";
import {MatTooltip} from "@angular/material/tooltip";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {MatIconButton} from "@angular/material/button";
import {ChatData, ChatService} from "../../../services/chat.service";
import {map, throwIfEmpty} from "rxjs";
import {ActivatedRoute, Params, Router} from "@angular/router";
import {toSignal} from "@angular/core/rxjs-interop";

@Component({
  selector: 'app-chat-drawer',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    MatFormField,
    MatLabel,
    MatSelect,
    MatIcon,
    MatOption,
    MatTooltip,
    NgClass,
    NgForOf,
    NgIf,
    MatIconButton
  ],
  templateUrl: './chat-drawer.component.html',
  styleUrl: './chat-drawer.component.scss'
})
export class ChatDrawerComponent {
  private activatedRoute = inject(ActivatedRoute)
  chatService = inject(ChatService)
  chatId$ = this.activatedRoute.params.pipe(map(
    data => Number(data["id"]) ?? 0
  ))
  chatId = toSignal(this.chatId$, {initialValue: 0} )
  router = inject(Router)
  fb = inject(FormBuilder)
  form = this.fb.group({
    language: [this.chatService.language(), Validators.required],
    model: [this.chatService.model(), Validators.required],
  });

  languages = [
    {display: 'Eesti', value: 'estonia'},
    {display: 'Inglise', value: 'english'},
  ];
  models = [
    {display: 'Väike', value: 'small'},
    {display: 'Suur', value: 'large'},
  ];

  // constructor() {
  //   effect(() => {
  //     console.log("chat id", this.chatId(), typeof this.chatId())
  //     for (const chat of this.chatService.chats()) {
  //       console.log("chat", chat.chat_id, typeof chat.chat_id )
  //     }
  //   })
  // }


  onSubmit() {
    if (this.form.valid) {
      this.chatService.language.set(this.form.value.language!)
      this.chatService.model.set(this.form.value.model!)
    } else {
      console.log('Form is invalid');
    }
  }

  onTitleChange(event: Event, chat: ChatData): void {
    const inputValue = (event.target as HTMLInputElement).value;
    // Update the title of the item
    chat.title = inputValue;
    this.chatService.chats.set([...this.chatService.chats()])
  }

  selectChat(id: number) {
    this.router.navigate(["chat", id])
  }

  toggleEdit(chat: ChatData) {
    if (chat.title === "") {
      return
    }

    if (chat.editing) {
      this.chatService.editChatTitle(chat.chat_id, chat.title).subscribe()
    }
    chat.editing = !chat.editing
  }
}
