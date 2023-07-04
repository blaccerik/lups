import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from "@angular/common/http";
import {ChatResponse} from "./chat.service";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class TestService {

  private url = 'api/test'

  constructor(private http: HttpClient) { }

  get(): Observable<string> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.get<string>(this.url, { headers: headers });
  }

  getId(): Observable<string> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.get<string>(this.url + "/69", { headers: headers });
  }

  post(): Observable<string> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { text: "dummy data" };
    return this.http.post<string>(this.url, body, { headers: headers });
  }

  getProtected(): Observable<string> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.get<string>(this.url + "/protected", { headers: headers });
  }

  getProtectedId(): Observable<string> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.get<string>(this.url + "/protected/69", { headers: headers });
  }

  postProtected(): Observable<string> {
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    const body = { text: "dummy data" };
    return this.http.post<string>(this.url + "/protected", body, { headers: headers });
  }

}
