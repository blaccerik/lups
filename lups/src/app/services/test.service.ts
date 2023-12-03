import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from "@angular/common/http";
import {Observable} from "rxjs";

@Injectable({
  providedIn: 'root'
})
export class TestService {

  private url = 'api/test'

  constructor(private http: HttpClient) {
  }

  get(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    return this.http.get<string>(this.url, {headers: headers});
  }

  getId(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    return this.http.get<string>(this.url + "/69", {headers: headers});
  }

  getQuery(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    const params = new HttpParams().set('page', 1);

    // Create an HTTP options object with headers
    const httpOptions = {
      headers: headers,
      params: params,
    }

    return this.http.get<string>(this.url + "/query", httpOptions);
  }

  post(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    const body = {text: "dummy data"};
    return this.http.post<string>(this.url, body, {headers: headers});
  }

  postForm(): Observable<string> {

    const text = "This is a dummy Blob.";
    const blob = new Blob([text], {type: 'text/plain'});

    const formData: FormData = new FormData();
    formData.append("test", "test")
    formData.append('file', blob);


    return this.http.post<string>(this.url + "/form", formData);
  }

  getForm(): Observable<Blob> {
    return this.http.get(this.url + "/form", {responseType: 'blob'});
  }

  getProtected(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    return this.http.get<string>(this.url + "/protected", {headers: headers});
  }

  getProtectedId(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    return this.http.get<string>(this.url + "/protected/69", {headers: headers});
  }

  postProtected(): Observable<string> {
    const headers = new HttpHeaders({'Content-Type': 'application/json'});
    const body = {text: "dummy data"};
    return this.http.post<string>(this.url + "/protected", body, {headers: headers});
  }

}
