import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor
} from '@angular/common/http';
import { Observable } from 'rxjs';
import {OAuthService} from "angular-oauth2-oidc";

@Injectable()
export class AuthInterceptor implements HttpInterceptor {

  constructor(private oauthService: OAuthService) {}

  intercept(request: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    if (this.oauthService.hasValidIdToken()) {
      if (request.url.startsWith("api")) {
        const accessToken = this.oauthService.getIdToken();
        const authReq = request.clone({
          setHeaders: {
            Authorization: `Bearer ${accessToken}`
          }
        });
        return next.handle(authReq);
      } else {
        console.log(request)
      }
    }
    const accessToken = this.oauthService.getIdToken();


    return next.handle(request);
  }
}
