import {Component, Inject, Input, Optional} from '@angular/core';
import {NavigationExtras, Router} from "@angular/router";
import {NewsService} from "../../../services/news.service";
import {MAT_DIALOG_DATA} from "@angular/material/dialog";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {OAuthService} from "angular-oauth2-oidc";

@Component({
  selector: 'app-create-news',
  templateUrl: './create-news.component.html',
  styleUrls: ['./create-news.component.scss']
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
    console.log(this.edit_id)
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
      const { title, text, category } = this.form.value;
      this.newsService.save(this.edit_id, title, text, category, this.edit_file).subscribe({
        next: (value: number) => {
          const currentUrl = this.router.url;
          this.router.navigate(["/news/" + value]).then(r => {
            if (!r) {
              window.location.reload()
            }
           })
        }
      })
    }
  }
}
