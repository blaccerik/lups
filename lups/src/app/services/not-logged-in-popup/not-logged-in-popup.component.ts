import {Component, Input} from '@angular/core';

@Component({
  selector: 'app-not-logged-in-popup',
  templateUrl: './not-logged-in-popup.component.html',
  styleUrls: ['./not-logged-in-popup.component.scss']
})
export class NotLoggedInPopupComponent {
  @Input() text: string;
}
