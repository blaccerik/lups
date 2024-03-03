import {Component, inject, OnInit, signal} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {ActivatedRoute, Router} from "@angular/router";
import {Answer, FamilyfeudService, Game, GameData, GameRound} from "../../../services/familyfeud.service";
import {MatDialog} from "@angular/material/dialog";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {MatButton, MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {MatIcon} from "@angular/material/icon";

@Component({
  selector: 'app-livegame',
  standalone: true,
  imports: [
    MatProgressSpinner,
    NgIf,
    MatButton,
    MatIcon,
    NgForOf,
    MatMiniFabButton,
    MatIconButton,
    NgClass
  ],
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
  loading = signal(true)
  strikes = signal(0)
  game = signal<GameData>({
    rounds: [],
    started: false,
    code: "",
    auth: ""
  })

  currentRound = signal<GameRound>({
    answers: [],
    question: "",
    round_number: -1
  })

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const code = params["id"]
      this.code.set(code)
      this.familyfeudService.getGameByCode(code).subscribe(
        data => {
          if (!data.started) {
            this.router.navigate(["/familyfeud/edit", data.code])
          }
          this.loading.set(false)
          this.game.set(data)
          this.currentRound.set(data.rounds[0])
        }
      )
    });
  }

  strike() {
    const value = this.strikes()
    if (value < 3) {
      this.strikes.set(value + 1)
    }
  }

  show(answer: Answer) {
    answer.revealed = !answer.revealed
  }

  move(backward: boolean) {
    const game = this.game()
    const gameRound  = this.currentRound()
    const index = game.rounds.indexOf(gameRound)
    if (backward && index > 0) {
      this.strikes.set(0)
      game.rounds.forEach(g => g.answers.forEach(a => a.revealed = false))
      this.game.set(game)
      this.currentRound.set(game.rounds[index - 1])
    } else if (!backward && index < game.rounds.length - 1) {
      this.strikes.set(0)
      game.rounds.forEach(g => g.answers.forEach(a => a.revealed = false))
      this.game.set(game)
      this.currentRound.set(game.rounds[index + 1])
    }
  }

  getRange(): number[] {
    return new Array(this.strikes()).fill(0).map((_, index) => index);
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

  protected readonly Array = Array;
}
