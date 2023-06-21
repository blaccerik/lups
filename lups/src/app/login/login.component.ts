import { Component } from '@angular/core';
import {Router} from "@angular/router";
import {ChatResponse, ChatService} from "../services/chat.service";
import {AuthService} from "../services/auth.service";

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  redirectLogin(): void {

    this.authService.login().subscribe({

      next: (response: string) => {
        window.location.href = response;
      },
      error: (error: any) => {
        console.log(error);
      }
    });

  }
}
