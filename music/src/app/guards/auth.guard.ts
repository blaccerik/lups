import {CanActivateFn, Router} from '@angular/router';
import {inject} from "@angular/core";
import {GoogleApiService} from "../services/google-api.service";
import {toObservable} from "@angular/core/rxjs-interop";
import {filter, map} from "rxjs";

export const authGuard: CanActivateFn = (route, state) => {
  const googleApiService = inject(GoogleApiService)
  const router = inject(Router)
  return toObservable(googleApiService.loggedIn).pipe(
    filter(value => {
      if (value === null) {
        return false
      }
      else if (!value) {
        router.navigate(["redirect"])
        return false
      }
      return true
    }),
    map(value => !!value),
  )
};
