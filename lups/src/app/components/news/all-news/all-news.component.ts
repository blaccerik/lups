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

  createImageFromBlob(image: Blob): Promise<string> {
    return new Promise((resolve) => {
      const reader = new FileReader();

      reader.addEventListener("load", () => {
        resolve(reader.result as string);
      }, false);

      reader.addEventListener("error", () => {
        resolve(""); // Return an empty string in case of an error
      });

      if (image) {
        reader.readAsDataURL(image);
      } else {
        resolve(""); // Return an empty string if no image is provided
      }
    });
  }

  loadNews(page: number): void {
    this.newsService.getAll(page).subscribe(newsData => {
      for (let item of newsData) {
        if (item.has_image) {
          this.newsService.getImage(String(item.id)).subscribe({
            next: async response => {
              item.image = await this.createImageFromBlob(response);
            },
            error: err => {
            }
          })
        }
        // 'item' is the current element of the array
      }
      this.newsItems = [...this.newsItems, ...newsData];
    });
  }

  selector: string = ".search-results";
  onScroll() {
    this.currentPage++;
    this.loadNews(this.currentPage)
  }

  click(id: number) {
    this.router.navigate(["/news/" + id])
  }
}
