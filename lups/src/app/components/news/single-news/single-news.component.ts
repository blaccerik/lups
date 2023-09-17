import { Component } from '@angular/core';
import {NewsResponse, NewsService} from "../../../services/news.service";
import {ActivatedRoute, Router} from "@angular/router";
import {UserInfoService} from "../../../services/user-info.service";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";
import {DomSanitizer} from "@angular/platform-browser";

@Component({
  selector: 'app-single-news',
  templateUrl: './single-news.component.html',
  styleUrls: ['./single-news.component.scss']
})
export class SingleNewsComponent {
  constructor(
    private route: ActivatedRoute,
    private newsService: NewsService,
    private userInfoService: UserInfoService,
    private router: Router,
    private formBuilder: FormBuilder,
    private sanitizer: DomSanitizer,
  ) {
    this.form = this.formBuilder.group({
      title: ["", [Validators.required, Validators.maxLength(100)]],
      text: ["", [Validators.required, Validators.maxLength(3000)]],
      category: ["", [Validators.required, Validators.maxLength(50)]]
    });
  }
  form: FormGroup;
  title = ""
  text = ""
  date = ""
  category = ""
  creator = ""
  creator_id = ""
  newsId = ""

  image: string | null
  imageFile: File | null

  isLoading: boolean
  notFound = false
  isEditing: boolean

  ngOnInit() {
    this.isLoading = true
    this.isEditing = false

    this.image = null
    this.imageFile = null

    this.route.paramMap.subscribe(params => {
      const id = params.get("id")
      if (id === null) {
        return
      }
      this.newsId = id
      this.newsService.get(id).subscribe({
        next: (newsResponse: NewsResponse) => {
          this.title = newsResponse.title
          this.creator = newsResponse.creator
          if (newsResponse.text) {
            this.text = newsResponse.text
          }
          this.creator_id = newsResponse.creator_id
          this.date = newsResponse.date
          this.category = newsResponse.category
          if (newsResponse.has_image) {
            this.getImage(id)
          } else {
            this.isLoading = false
          }
        },
        error: err => {
          this.isLoading = false
          this.notFound = true
        }
      })
    })
  }

  getImage(id: string) {
    this.newsService.getImage(id).subscribe({
      next: response => {
        this.image = URL.createObjectURL(response);
        this.imageFile = new File([response], "image.jpg", { type: response.type });
        this.isLoading = false;
      },
      error: err => {
        console.log(err)
        this.isLoading = false;
        this.image = null
      }
    })
  }
  canEdit(): boolean {
    return this.userInfoService.googleId === this.creator_id
  }

  edit() {
    this.isEditing = true
  }
}
