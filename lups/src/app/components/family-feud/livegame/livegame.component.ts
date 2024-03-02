import {Component, inject, OnInit, signal} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {ActivatedRoute, Router} from "@angular/router";
import {FamilyfeudService} from "../../../services/familyfeud.service";
import {MatDialog} from "@angular/material/dialog";

@Component({
  selector: 'app-livegame',
  standalone: true,
  imports: [],
  templateUrl: './livegame.component.html',
  styleUrl: './livegame.component.scss'
})
export class LivegameComponent implements OnInit {
  private oauthService = inject(OAuthService)
  private router = inject(Router)
  private familyfeudService = inject(FamilyfeudService)
  private dialog = inject(MatDialog)
  private route = inject(ActivatedRoute)

  code = signal<string | null>(null)

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.code.set(params["id"])
    });
  }

  stop() {
    const code = this.code()
    if (code) {
      this.familyfeudService.setGameStatus(code, false).subscribe(
        data => {
          this.router.navigate(["/familyfeud/edit", data.code])
        }
      )
    }
  }
}
