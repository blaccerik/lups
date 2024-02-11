import { Component } from '@angular/core';
import {MatDialogRef} from "@angular/material/dialog";
import {FormsModule} from "@angular/forms";

@Component({
  selector: 'app-gamecode',
  standalone: true,
  imports: [
    FormsModule
  ],
  templateUrl: './gamecode.component.html',
  styleUrl: './gamecode.component.scss'
})
export class GamecodeComponent {
  userInput: string;

  constructor(public dialogRef: MatDialogRef<GamecodeComponent>,) {}

  onSendClick(): void {
    this.dialogRef.close(this.userInput);
  }
}
