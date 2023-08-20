import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {catchError, Observable, of} from "rxjs";


export interface NewsResponse {
  creator: string,
  title: string,
  text: string
  creator_id: string
}

@Injectable({
  providedIn: 'root'
})
export class NewsService {

  private url = 'api/news'

  constructor(private http: HttpClient) { }

  create(title: string, text: string, file: File | null): Observable<number> {
    const formData: FormData = new FormData();
    formData.append('title', title);
    formData.append('text', text);
    if (file) {
      formData.append('file', file, file.name);
    }
    return this.http.post<number>(this.url + "/create", formData)
  }

  update(id: string, title: string, text: string, new_file: boolean, file: File | null): Observable<any> {
    const formData: FormData = new FormData();
    formData.append('title', title);
    formData.append('text', text);
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

  getImage(id: string): Observable<Blob> {
    return this.http.get(this.url + "/" + id + "/image",  { responseType: 'blob' })
  }
}
