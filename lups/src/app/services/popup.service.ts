import { Injectable } from '@angular/core';
import {NotLoggedInPopupComponent} from "./not-logged-in-popup/not-logged-in-popup.component";

@Injectable({
  providedIn: 'root'
})
export class PopupService {

  private popups: string[] = [];
  private maxPopups = 3;
  private popupTimeoutDuration = 1000;
  private timeoutId: any = null;

  constructor() {}

  addPopup(text: string): void {
    if (this.popups.length >= this.maxPopups) {
      return; // Limit reached, do not add more popups
    }
    this.popups.push(text);

    if (!this.timeoutId) {
      this.timeoutId = setTimeout(() => {
        this.removePopup();
      }, this.popupTimeoutDuration);
    }
  }

  removePopup(): void {
    if (this.popups.length > 0) {
      this.popups.shift();
      if (this.popups.length > 0) {
        this.timeoutId = setTimeout(() => {
          this.removePopup();
        }, this.popupTimeoutDuration);
      } else {
        this.timeoutId = null;
      }
    }
  }

  getPopups(): string[] {
    return this.popups;
  }
}
