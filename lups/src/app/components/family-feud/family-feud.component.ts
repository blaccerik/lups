import {Component, inject, OnInit, signal} from '@angular/core';
import {MatDialog, MatDialogRef} from "@angular/material/dialog";
import {GamecodeComponent} from "./gamecode/gamecode.component";
import {FormsModule} from "@angular/forms";
import {NgForOf, NgIf} from "@angular/common";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {GameBoardComponent} from "./gameboard/game-board.component";
import {ActivatedRoute, Router} from "@angular/router";
import {GamebannerComponent} from "./gamebanner/gamebanner.component";
import {GamelistComponent} from "./gamelist/gamelist.component";
import {OAuthService} from "angular-oauth2-oidc";
import {FamilyfeudService, Game} from "../../services/familyfeud.service";

@Component({
  selector: 'app-family-feud',
  standalone: true,
  imports: [
    FormsModule,
    NgIf,
    MatProgressSpinner,
    GameBoardComponent,
    GamebannerComponent,
    NgForOf
  ],
  templateUrl: './family-feud.component.html',
  styleUrl: './family-feud.component.scss'
})
export class FamilyFeudComponent {

  private oauthService = inject(OAuthService)
  private router = inject(Router)
  private familyfeudService = inject(FamilyfeudService)
  private dialog = inject(MatDialog)
  create() {
    if (!this.oauthService.hasValidIdToken()) {
      localStorage.setItem('originalUrl', window.location.pathname);
      this.oauthService.initLoginFlow('google');
      return
    }
    this.familyfeudService.createGame().subscribe(
      game => {
        this.router.navigate(['/familyfeud/edit', game.code]);
      }
    )
  }

  games() {
    this.dialog.open(GamelistComponent);
  }

  join() {
    this.dialog.open(GamecodeComponent);
  }
}
