import {Component, Inject, Optional} from '@angular/core';
import {Router} from "@angular/router";
import {NewsService} from "../../../services/news.service";
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {OAuthService} from "angular-oauth2-oidc";

@Component({
  selector: 'app-news',
  templateUrl: './create-news.component.html',
  styleUrls: ['./create-news.component.scss']
})
export class CreateNewsComponent {

  constructor(
    private newsService: NewsService,
    private router: Router,
    private formBuilder: FormBuilder,
    private oauthService: OAuthService,
  ) {

    if (!this.oauthService.hasValidIdToken()) {
      this.oauthService.initLoginFlow('google');
    }

    this.form = this.formBuilder.group({
      title: ["", [Validators.required, Validators.maxLength(100)]],
      text: ["", [Validators.required, Validators.maxLength(3000)]],
      category: ["", [Validators.required, Validators.maxLength(50)]]
    });
  }
  form: FormGroup;
  imageEdit: any
  selectedFile: File | null

  onFileChange(event: any) {
    const fileList: FileList = event.target.files;
    if (fileList.length > 0) {
      this.selectedFile = fileList[0];
      this.convertImageToBase64(this.selectedFile)
    }
  }

  convertImageToBase64(file: File) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      this.imageEdit = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  remove() {
    this.selectedFile = null
    this.imageEdit = null
  }

  save() {
    if (this.form.valid) {
      const { title, text, category } = this.form.value;
      this.newsService.create(title, text, category, this.selectedFile).subscribe({
        next: (value: number) => {
          this.router.navigate(["/news/" + value])
        }
      })
    }
  }
}
