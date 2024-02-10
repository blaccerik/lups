import { Component } from '@angular/core';
import {MatDialogContent, MatDialogRef} from "@angular/material/dialog";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton} from "@angular/material/button";

@Component({
  selector: 'app-help-dialog',
  standalone: true,
  imports: [
    MatDialogContent,
    MatDialogContent,
    MatIcon,
    MatIcon,
    MatIconButton,
    MatIconButton
  ],
  templateUrl: './help-dialog.component.html',
  styleUrl: './help-dialog.component.scss'
})
export class HelpDialogComponent {
  constructor(
    private dialogRef: MatDialogRef<HelpDialogComponent>,
  ) {}

  closeDialog() {
    this.dialogRef.close();
  }
}
