import { CanActivateFn } from '@angular/router';
import {inject} from "@angular/core";
import {OAuthService} from "angular-oauth2-oidc";

export const authGuard: CanActivateFn = (route, state) => {
  const oauthService = inject(OAuthService)
  if (!oauthService.hasValidIdToken()) {
    localStorage.setItem('originalUrl', window.location.pathname);
    oauthService.initLoginFlow('google');
    return false
  }
  return true;
};
