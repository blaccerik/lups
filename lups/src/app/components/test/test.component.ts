import { Component } from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {TestService} from "../../services/test.service";

@Component({
  selector: 'app-test',
  templateUrl: './test.component.html',
  styleUrls: ['./test.component.scss']
})
export class TestComponent {

  get: string = "get"
  getId: string = "getId"
  post: string = "post"
  getProtected: string = "getProtected"
  getProtectedId: string = "getProtectedId"
  postProtected: string = "postProtected"

  constructor(public oauthService: OAuthService, private testService: TestService) {}

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
    this.testService.post().subscribe({
      next: (value: string) => {
        this.post = value
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
}
