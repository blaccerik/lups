import {Component, Input} from '@angular/core';
import {MatButton} from "@angular/material/button";
import {MatCard, MatCardActions, MatCardContent, MatCardHeader, MatCardTitle} from "@angular/material/card";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatInput} from "@angular/material/input";
import {MatOption} from "@angular/material/autocomplete";
import {MatSelect} from "@angular/material/select";
import {NgIf} from "@angular/common";
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from "@angular/forms";
import {Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {NewsId, NewsService} from "../../../services/news.service";

@Component({
  selector: 'app-create-news',
  standalone: true,
  imports: [
    MatButton,
    MatButton,
    MatCard,
    MatCard,
    MatCardActions,
    MatCardActions,
    MatCardContent,
    MatCardContent,
    MatCardHeader,
    MatCardHeader,
    MatCardTitle,
    MatCardTitle,
    MatError,
    MatError,
    MatFormField,
    MatFormField,
    MatIcon,
    MatIcon,
    MatInput,
    MatInput,
    MatLabel,
    MatLabel,
    MatOption,
    MatOption,
    MatSelect,
    MatSelect,
    NgIf,
    NgIf,
    ReactiveFormsModule,
    ReactiveFormsModule
  ],
  templateUrl: './create-news.component.html',
  styleUrl: './create-news.component.scss'
})
export class CreateNewsComponent {
  @Input() edit_file: File | null;
  @Input() edit_title: string;
  @Input() edit_text: string;
  @Input() edit_cat: string;
  @Input() edit_id: string;


  constructor(
    private newsService: NewsService,
    private router: Router,
    private formBuilder: FormBuilder,
    private oauthService: OAuthService,
  ) {
    if (!this.oauthService.hasValidIdToken()) {
      this.oauthService.initLoginFlow('google');
    }
  }

  form: FormGroup;
  image: string | null

  ngOnInit() {
    this.form = this.formBuilder.group({
      title: [this.edit_title, [Validators.required, Validators.maxLength(100)]],
      text: [this.edit_text, [Validators.required, Validators.maxLength(3000)]],
      category: [this.edit_cat, [Validators.required, Validators.maxLength(25)]]
    });
    this.image = null
    if (this.edit_file) {
      this.image = URL.createObjectURL(this.edit_file);
    }
  }

  onFileChange(event: any) {
    const fileList: FileList = event.target.files;
    if (fileList.length > 0) {
      this.edit_file = fileList[0]
      this.image = URL.createObjectURL(this.edit_file);
    }
  }

  remove() {
    this.image = null
    this.edit_file = null
  }

  save() {
    if (this.form.valid) {
      const {title, text, category} = this.form.value;
      this.newsService.save(this.edit_id, title, text, category, this.edit_file).subscribe({
        next: (value: NewsId) => {
          this.router.navigate(["/news/" + value.id]).then(r => {
            if (!r) {
              window.location.reload()
            }
          })
        }
      })
    }
  }

  hasError(path: string, errorCode: string) {
    return this.form && this.form.hasError(errorCode, path);
  }
}
