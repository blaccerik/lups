import {Component, inject} from '@angular/core';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatFormField, MatLabel} from "@angular/material/form-field";
import {MatOption, MatSelect} from "@angular/material/select";
import {MatIcon} from "@angular/material/icon";
import {MatTooltip} from "@angular/material/tooltip";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {MatIconButton} from "@angular/material/button";
import {ChatService} from "../../../services/chat.service";

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
  chatService = inject(ChatService)
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
}
