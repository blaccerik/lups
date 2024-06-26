import {Component, inject} from '@angular/core';
import {FormBuilder, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatIcon} from "@angular/material/icon";
import {MatTooltip} from "@angular/material/tooltip";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {MatIconButton} from "@angular/material/button";
import {ChatData, ChatService} from "../../../services/chat.service";
import {ActivatedRoute, Params, Router} from "@angular/router";
import {toSignal} from "@angular/core/rxjs-interop";
import {MatDivider} from "@angular/material/divider";
import {MatProgressSpinner} from "@angular/material/progress-spinner";

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
    MatIconButton,
    MatDivider,
    MatProgressSpinner
  ],
  templateUrl: './chat-drawer.component.html',
  styleUrl: './chat-drawer.component.scss'
})
export class ChatDrawerComponent {
  private activatedRoute = inject(ActivatedRoute)
  chatService = inject(ChatService)
  route$ = this.activatedRoute.params
  route = toSignal(this.route$, {initialValue: {} as Params})

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

  selectChat(chat: ChatData) {
    if (!chat.editing) {
      this.router.navigate(["chat", chat.chat_id])
    }
  }

  toggleEdit(event: MouseEvent, chat: ChatData) {
    event.stopPropagation();
    if (chat.title === "") {
      return
    }

    if (chat.editing) {
      this.chatService.editChatTitle(chat.chat_id, chat.title).subscribe()
    }
    chat.editing = !chat.editing
    this.chatService.chats.set([...this.chatService.chats()])
  }

  protected readonly Number = Number;
}
