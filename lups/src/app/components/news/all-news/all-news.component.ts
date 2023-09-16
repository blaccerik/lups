import {Component, ElementRef, HostListener} from '@angular/core';
import {NewsResponse, NewsService} from "../../../services/news.service";
import {ActivatedRoute, Router} from "@angular/router";
import {UserInfoService} from "../../../services/user-info.service";
import {FormBuilder, Validators} from "@angular/forms";


@Component({
  selector: 'app-all-news',
  templateUrl: './all-news.component.html',
  styleUrls: ['./all-news.component.scss']
})
export class AllNewsComponent {

  constructor(
    private route: ActivatedRoute,
    private newsService: NewsService,
    private router: Router,
    private el: ElementRef
  ) {}

  currentPage: number
  newsItems: NewsResponse[] = []

  ngOnInit() {
    this.currentPage = 0
    this.loadNews(this.currentPage);
  }

  createImageFromBlob(image: Blob) {
    let reader = new FileReader();
    reader.addEventListener("load", () => {
      reader.result
    }, false);

    if (image) {
      reader.readAsDataURL(image);
    }
  }

  loadNews(page: number): void {
    this.newsService.getAll(page).subscribe(newsData => {
      for (let item of newsData) {
        this.newsService.getImage(String(item.id)).subscribe({
          next: response => {
            this.createImageFromBlob(response);
          },
          error: err => {
          }
        })
        // 'item' is the current element of the array
      }
      const newer = newsData.forEach(function (newsResponse: NewsResponse) {
        console.log(newsResponse)
        return newsResponse
      })
      console.log(newer)
      this.newsItems = [...this.newsItems, ...newsData];
    });
  }

  selector: string = ".search-results";
  onScroll() {
    this.currentPage++;
    this.loadNews(this.currentPage)
    console.log("scrolled!!");
  }
}
