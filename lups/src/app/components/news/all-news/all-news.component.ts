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
    this.loadNews();
  }

  loadNews(): void {
    this.newsService.getAll(this.currentPage).subscribe(newsData => {
      this.newsItems = [...this.newsItems, ...newsData];
    });
  }

  selector: string = ".search-results";
  onScroll() {
    console.log("scrolled!!");
  }
}
