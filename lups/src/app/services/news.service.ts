import { Injectable } from '@angular/core';
import {HttpClient, HttpParams} from "@angular/common/http";
import {catchError, Observable, of} from "rxjs";


export interface NewsResponse {
  category: string,
  creator: string,
  creator_id: string,
  date: string,
  text: string,
  title: string
}

@Injectable({
  providedIn: 'root'
})
export class NewsService {

  private url = 'api/news'

  constructor(private http: HttpClient) { }

  create(title: string, text: string, category: string, file: File | null): Observable<number> {
    const formData: FormData = new FormData();
    formData.append('title', title);
    formData.append('text', text);
    formData.append("category", category)
    if (file) {
      formData.append('file', file, file.name);
    }
    return this.http.post<number>(this.url + "/create", formData)
  }

  update(id: string, title: string, text: string, category: string, new_file: boolean, file: File | null): Observable<any> {
    const formData: FormData = new FormData();
    formData.append('title', title);
    formData.append('text', text);
    formData.append("category", category);
    if (new_file) {
      formData.append("new_file", "true")
    }
    if (file) {
      formData.append('file', file);
    }
    return this.http.put<number>(this.url + "/" + id, formData)
  }

  get(id: string): Observable<NewsResponse> {
    return this.http.get<NewsResponse>(this.url + "/" + id)
  }

  getAll(page: number): Observable<NewsResponse[]> {
    const params = new HttpParams().set('page', page.toString());
    return this.http.get<NewsResponse[]>(this.url, { params})
  }

  getImage(id: string): Observable<Blob> {
    return this.http.get(this.url + "/" + id + "/image",  { responseType: 'blob' })
  }
}
