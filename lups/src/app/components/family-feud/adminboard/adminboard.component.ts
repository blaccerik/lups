import {Component, computed, inject, OnInit, signal} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {ActivatedRoute, Router} from "@angular/router";
import {Answer, FamilyfeudService, GameRound} from "../../../services/familyfeud.service";
import {MatDialog} from "@angular/material/dialog";
import {NgForOf, NgIf} from "@angular/common";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";

@Component({
  selector: 'app-adminboard',
  standalone: true,
  imports: [
    NgIf,
    MatProgressSpinner,
    NgForOf,
    MatIcon,
    MatIconButton,
    MatMiniFabButton,
    FormsModule,
    MatFormField,
    MatLabel,
    MatInput,
    MatError,
    ReactiveFormsModule
  ],
  templateUrl: './adminboard.component.html',
  styleUrl: './adminboard.component.scss'
})
export class AdminboardComponent implements OnInit {
  private oauthService = inject(OAuthService)
  private router = inject(Router)
  private familyfeudService = inject(FamilyfeudService)
  private dialog = inject(MatDialog)
  private route = inject(ActivatedRoute)


  gameData = signal<GameRound[]>([])
  loading = signal(true)
  code = signal<string | null>(null)

  totalRounds = computed(() => 3)

  totalQuestions = computed(() => 3);


  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const code = params["id"]
      this.code.set(code)
      this.familyfeudService.getGameByCode(code).subscribe(
        data => {
          console.log(data)
          this.gameData.set(data)
          this.loading.set(false)
        }
      )
    });
  }

  removeRound(gameRound: GameRound) {
    this.gameData.update(rounds => {
        const filteredRounds = rounds.filter(round => round !== gameRound)
        for (let i = 0; i < filteredRounds.length; i++) {
          filteredRounds[i].round_number = i + 1
        }
        return filteredRounds
      }
    )
  }

  addRound() {
    this.gameData.update(items => [...items, {
      answers: [],
      round_number: items.length + 1,
      question: ""
    }])
  }

  addQuestion(gameRound: GameRound) {
    this.gameData.update(items => {
      for (const round of this.gameData()) {
        if (round === gameRound) {
          round.answers.push({
            points: 1,
            text: "tere"
          })
          break
        }
      }
      return [...items]
    })
  }

  removeQuestion(gameRound: GameRound, question: Answer) {
    this.gameData.update(items => {
      for (const round of this.gameData()) {
        if (round === gameRound) {
          round.answers = round.answers.filter(q => q !== question)
          break
        }
      }
      return [...items]
    })
  }

  moveRound(gameRound: GameRound, up: boolean) {
    const data = this.gameData()
    const current = gameRound.round_number
    if (up && current > 1) {
      const otherRound = data[current - 2]
      otherRound.round_number = current
      gameRound.round_number = current - 1
    } else if (!up && current < data.length) {
      const otherRound = data[current]
      otherRound.round_number = current
      gameRound.round_number = current + 1
    }
    this.gameData.update(gameRounds =>
      gameRounds.sort((a, b) => a.round_number - b.round_number)
    )
  }

  toggleEditQuestion(gameRound: GameRound) {
    gameRound.editing = !gameRound.editing
  }

  toggleEditAnswer(answer: Answer) {
    answer.editing = !answer.editing
  }

  hasError() {
    const gameRounds = this.gameData()
    if (gameRounds.length == 0 || gameRounds.length > 10) {
      return true
    }
    for (const gameRound of gameRounds) {
      // check if question is okay
      if (gameRound.editing || this.hasErrorText(gameRound.question)) {
        return true
      }

      let points = 0
      for (const answer of gameRound.answers) {
        if (answer.editing || this.hasErrorText(answer.text)) {
          return true
        }
        points += answer.points
      }

      if (points !== 100) {
        return true
      }
    }

    return false
  }

  hasErrorText(text: string) {
    return text.length == 0
  }

  save() {
    const error = this.hasError()
    const code = this.code()
    if (code) {
      this.familyfeudService.postGameByCode(code, this.gameData()).subscribe(
        data => {
          console.log(data)
        }
      )
    }
  }
}
