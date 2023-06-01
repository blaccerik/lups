import { Component } from '@angular/core';


interface section {
  text: string;
  link: string;
}

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent {
  sections: section[] = [
    {text: "Raha", link: ""},
    {text: "Naised", link: ""},
    {text: "Carlos", link: ""},
  ]
}
