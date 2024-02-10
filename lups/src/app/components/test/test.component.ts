import { Component } from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {TestService} from "../../services/test.service";

@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.scss']
})
export class TestComponent {

  get= ""
  getId= ""
  query = ""
  post= ""
  postForm = ""
  getForm = ""
  getProtected: string = "getProtected"
  getProtectedId: string = "getProtectedId"
  postProtected: string = "postProtected"

  constructor(public oauthService: OAuthService, public testService: TestService) {}

  ngOnInit() {
    this.testService.get().subscribe({
      next: (value: string) => {
        this.get = value
      },
      error: err => {console.log(err)}
    })
    this.testService.getId().subscribe({
      next: (value: string) => {
        this.getId = value
      },
      error: err => {console.log(err)}
    })
    this.testService.getQuery().subscribe({
      next: (value: string) => {
        this.query = value
      },
      error: err => {console.log(err)}
    })

    this.testService.post().subscribe({
      next: (value: string) => {
        this.post = value
      },
      error: err => {console.log(err)}
    })

    this.testService.postForm().subscribe({
      next: (value: string) => {
        this.postForm = value
      },
      error: err => {console.log(err)}
    })

    this.testService.getForm().subscribe({
      next: async (value: Blob) => {
        const text: string = await this.readBlobAsText(value);
        this.getForm = text
      },
      error: err => {console.log(err)}
    })


    this.testService.getProtected().subscribe({
      next: (value: string) => {
        this.getProtected = value
      },
      error: err => {console.log(err)}
    })
    this.testService.getProtectedId().subscribe({
      next: (value: string) => {
        this.getProtectedId = value
      },
      error: err => {console.log(err)}
    })
    this.testService.postProtected().subscribe({
      next: (value: string) => {
        this.postProtected = value
      },
      error: err => {console.log(err)}
    })
  }

  private readBlobAsText(blob: Blob): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => {
        const text = reader.result as string;
        resolve(text);
      };

      reader.onerror = (error) => {
        reject(error);
      };

      reader.readAsText(blob);
    });
  }
}
