import {Component, inject, OnInit} from '@angular/core';
import {MatDialogRef} from "@angular/material/dialog";
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {MatFormField, MatHint, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {MatIcon} from "@angular/material/icon";
import {MatMiniFabButton} from "@angular/material/button";
import {Router} from "@angular/router";

@Component({
  selector: 'app-gamecode',
  standalone: true,
  imports: [
    FormsModule,
    MatLabel,
    MatInput,
    MatHint,
    MatFormField,
    MatIcon,
    MatMiniFabButton,
    ReactiveFormsModule
  ],
  templateUrl: './gamecode.component.html',
  styleUrl: './gamecode.component.scss'
})
export class GamecodeComponent implements OnInit {

  router = inject(Router)
  dialogRef = inject(MatDialogRef<GamecodeComponent>)
  form: FormGroup;

  ngOnInit(): void {
    this.form = new FormGroup({
      code: new FormControl("", [
        Validators.required,
        Validators.minLength(4),
        Validators.maxLength(4)
      ]),
    });
  }

  onEnterPress(): void {
    this.dialogRef.close();
    if (this.form.valid) {
      const code = this.form.get('code')!.value.toLowerCase();
      this.router.navigate(['/familyfeud', code]);
    }
  }
}
