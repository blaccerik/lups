import { Component } from '@angular/core';
import {NewsResponse, NewsService} from "../../../services/news.service";
import {ActivatedRoute, Router} from "@angular/router";
import {UserInfoService} from "../../../services/user-info.service";
import {FormBuilder, FormGroup, Validators} from "@angular/forms";

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
  ) {
    this.form = this.formBuilder.group({
      title: ["", [Validators.required, Validators.maxLength(100)]],
      text: ["", [Validators.required, Validators.maxLength(3000)]]
    });
  }
  form: FormGroup;
  title = ""
  text = ""
  creator = ""
  creator_id = ""
  newsId = ""

  image: any
  imageEdit: any
  selectedFile: File | null
  fileHasChanged: boolean
  isLoading: boolean
  isEditing: boolean

  ngOnInit() {
    this.isLoading = true
    this.image = null
    this.selectedFile = null
    this.isEditing = false
    this.fileHasChanged = false;
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
          this.text = newsResponse.text
          this.creator_id = newsResponse.creator_id
          this.getImage(id)
        }
      })
    })
  }

  getImage(id: string) {
    this.newsService.getImage(id).subscribe({
      next: response => {
        this.createImageFromBlob(response);
        this.isLoading = false;
      },
      error: err => {
        this.isLoading = false;
        this.image = null
      }
    })
  }

  createImageFromBlob(image: Blob) {
    let reader = new FileReader();
    reader.addEventListener("load", () => {
      this.image = reader.result
    }, false);

    if (image) {
      reader.readAsDataURL(image);
    }
  }

  convertImageToBase64(file: File) {
    const reader = new FileReader();
    reader.onload = (e: any) => {
      this.imageEdit = e.target.result;
    };
    reader.readAsDataURL(file);
  }

  onFileChange(event: any) {
    const fileList: FileList = event.target.files;
    if (fileList.length > 0) {
      this.selectedFile = fileList[0];
      this.fileHasChanged = true;
      this.convertImageToBase64(this.selectedFile)
    }
  }

  canEdit(): boolean {
    return this.userInfoService.googleId === this.creator_id
  }

  edit() {
    this.isEditing = true
    this.form.patchValue({
      title: this.title,
      text: this.text
    });
    this.imageEdit = this.image
  }

  save() {
    if (this.form.valid) {
      const { title, text } = this.form.value;
      this.newsService.update(this.newsId, title, text, this.fileHasChanged, this.selectedFile).subscribe({
        next: value => {
          this.title = title
          this.text = text
          this.isEditing = false
          this.selectedFile = null
          this.image = this.imageEdit
          this.imageEdit = null
          this.fileHasChanged = false
        }
      })
    }
  }

  remove() {
    this.fileHasChanged = true;
    this.selectedFile =  null
    this.imageEdit = null
  }

  discard() {
    this.isEditing = false
    this.imageEdit = null
    this.selectedFile = null
    this.fileHasChanged = false
  }
}
