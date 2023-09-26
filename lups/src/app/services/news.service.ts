import { Injectable } from '@angular/core';
import {HttpClient, HttpParams} from "@angular/common/http";
import {catchError, Observable, of} from "rxjs";


export interface NewsResponse {
  id: number,
  category: string,
  creator: string,
  creator_id: string,
  date: string,
  text?: string,
  image?: string
  title: string

  has_image: boolean
  loading: boolean
}

@Injectable({
  providedIn: 'root'
})
export class NewsService {

  private url = 'api/news';

  constructor(private http: HttpClient) { }

  save(id: string | null, title: string, text: string, category: string, file: File | null): Observable<number> {
    const formData: FormData = new FormData();
    formData.append('title', title);
    formData.append('text', text);
    formData.append("category", category)
    if (file) {
      formData.append('file', file, file.name);
    }
    if (id) {
      return this.http.put<number>(this.url + "/" + id, formData)
    } else {
      return this.http.post<number>(this.url + "/create", formData)
    }
  }

  get(id: string): Observable<NewsResponse> {
    return this.http.get<NewsResponse>(this.url + "/" + id)
  }

  getAll(page: number): Observable<NewsResponse[]> {
    const params = new HttpParams().set('page', page.toString());
    console.log(this.url)
    return this.http.get<NewsResponse[]>(this.url + "/", { params })
  }

  getImage(id: string): Observable<Blob> {
    return this.http.get(this.url + "/" + id + "/image",  { responseType: 'blob' })
  }
}
