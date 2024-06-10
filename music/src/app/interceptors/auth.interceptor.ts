import {HttpInterceptorFn} from '@angular/common/http';
import {inject} from "@angular/core";
import {OAuthService} from "angular-oauth2-oidc";

export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const oauthService = inject(OAuthService);
  if (oauthService.hasValidIdToken()) {
    if (req.url.startsWith("api")) {
      const accessToken = oauthService.getIdToken();
      const authReq = req.clone({
        setHeaders: {
          Authorization: `Bearer ${accessToken}`
        }
      });
      return next(authReq);
    }
  }

  // todo remove this
  const authReq = req.clone({
    setHeaders: {
      Authorization: `Bearer erik`
    }
  });
  return next(authReq);

  return next(req);
};
