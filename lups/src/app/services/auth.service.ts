import { Injectable } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private url = '/api/auth/login'; // Replace with your server endpoint

  constructor(private http: HttpClient) { }

  login(): Observable<string> {
    return this.http.get<string>(this.url)
  }
}
