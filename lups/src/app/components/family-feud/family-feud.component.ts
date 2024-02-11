import { Component } from '@angular/core';
import {MatDialog} from "@angular/material/dialog";
import {GamecodeComponent} from "./gamecode/gamecode.component";

@Component({
  selector: 'app-family-feud',
  standalone: true,
  imports: [],
  templateUrl: './family-feud.component.html',
  styleUrl: './family-feud.component.scss'
})
export class FamilyFeudComponent {

  constructor(public dialog: MatDialog) {
  }

  create() {

  }

  join() {
    const dialogRef = this.dialog.open(GamecodeComponent);

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed');
      console.log(result)
    });
  }
}
