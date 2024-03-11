import {Component, inject, OnInit, signal} from '@angular/core';
import {FormsModule} from "@angular/forms";
import {FamilyfeudService, Game} from "../../../services/familyfeud.service";
import {NgForOf, NgIf} from "@angular/common";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {OAuthService} from "angular-oauth2-oidc";
import {MatDialogRef} from "@angular/material/dialog";
import {Router} from "@angular/router";

@Component({
  selector: 'app-gamelist',
  standalone: true,
  imports: [
    FormsModule,
    NgForOf,
    MatProgressSpinner,
    NgIf
  ],
  templateUrl: './gamelist.component.html',
  styleUrl: './gamelist.component.scss'
})
export class GamelistComponent implements OnInit {

  private oauthService = inject(OAuthService)
  private router = inject(Router)
  private familyfeudService = inject(FamilyfeudService)
  private dialogRef = inject(MatDialogRef<GamelistComponent>)
  games = signal<null | Game[]>(null)

  ngOnInit(): void {
    this.dialogRef.updateSize('40%', '40%');
    if (!this.oauthService.hasValidIdToken()) {
      localStorage.setItem('originalUrl', window.location.pathname);
      this.oauthService.initLoginFlow('google');
      return
    }

    this.familyfeudService.getGames().subscribe(
      data => this.games.set(data)
    )
  }

  click(code: string) {
    this.dialogRef.close()
    this.router.navigate(['/familyfeud/edit', code])
  }
}
