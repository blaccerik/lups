import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class UserInfoService {
  get googleId(): string {
    return this._googleId;
  }

  set googleId(value: string) {
    this._googleId = value;
  }
  get userName(): string {
    return this._userName;
  }
  set userName(value: string) {
    this._userName = value;
  }
  get picture(): string {
    return this._picture;
  }
  set picture(value: string) {
    this._picture = value;
  }
  private _userName: string;
  private _picture: string;
  private _googleId: string;

}
