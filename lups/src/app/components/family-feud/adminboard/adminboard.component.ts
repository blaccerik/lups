import {Component, computed, inject, OnInit, signal} from '@angular/core';
import {OAuthService} from "angular-oauth2-oidc";
import {ActivatedRoute, Router} from "@angular/router";
import {Answer, FamilyfeudService, GameRound} from "../../../services/familyfeud.service";
import {MatDialog} from "@angular/material/dialog";
import {NgForOf, NgIf} from "@angular/common";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {MatIcon} from "@angular/material/icon";
import {MatButton, MatFabButton, MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {FormsModule, ReactiveFormsModule} from "@angular/forms";
import {MatError, MatFormField, MatLabel} from "@angular/material/form-field";
import {MatInput} from "@angular/material/input";
import {MatTooltip} from "@angular/material/tooltip";

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
    ReactiveFormsModule,
    MatTooltip,
    MatFabButton,
    MatButton
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
  counter = signal(0)
  totalRounds = computed(() => this.gameData().length)
  totalQuestions = computed(() =>
    this.gameData().reduce((sum, round) => sum + round.answers.length, 0));

  undo() {
    const code = this.code()
    if (!code) {
      return
    }
    this.loading.set(true)
    this.familyfeudService.getGameByCode(code).subscribe(
      data => {
        if (data.started) {
          this.router.navigate(["/familyfeud/admin", data.code])
        }
        this.gameData.set(data.rounds)
        this.loading.set(false)
        this.counter.set(data.rounds.length)
      }
    )
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.code.set(params["id"])
      this.undo()
    });
  }

  removeRound(gameRound: GameRound) {
    this.gameData.update(rounds => {
        return rounds.filter(round => round !== gameRound)
      }
    )
  }

  addRound() {
    this.gameData.update(items => [...items, {
      answers: [],
      round_number: this.counter() + 1,
      question: ""
    }])
    this.counter.set(this.counter() + 1)
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
    const index = data.indexOf(gameRound)

    // const current = gameRound.round_number
    if (!up && index < data.length - 1) {
      const otherRound = data[index + 1]
      data[index + 1] = gameRound
      data[index] = otherRound
    } else if (up && index > 0) {
      const otherRound = data[index - 1]
      data[index - 1] = gameRound
      data[index] = otherRound
    }
    this.gameData.update(() => data)
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

  dontAddUp(gameRound: GameRound) {
    return gameRound.answers.map(a => a.points)
      .reduce((partialSum, a) => partialSum + a, 0) !== 100;
  }

  canAddAnswer(gameRound: GameRound) {
    return gameRound.answers.length < 10
  }

  canAddRound() {
    return this.gameData().length < 10
  }

  onInputChange(answer: Answer) {
    if (answer.points < 1) {
      answer.points = 1;
    } else if (answer.points > 100) {
      answer.points = 100;
    }
  }

  start() {
    const error = this.hasError()
    const code = this.code()
    if (code && !error) {
      this.familyfeudService.setGameStatus(code, true).subscribe(
        data => {
          this.router.navigate(["/familyfeud/admin", data.code])
          console.log(data)
        }
      )
    }
  }

  save() {
    const error = this.hasError()
    const code = this.code()
    if (code && !error) {
      this.loading.set(true)
      this.familyfeudService.postGameByCode(code, this.gameData()).subscribe(
        data => {
          this.gameData.set(data.rounds)
          this.loading.set(false)
          this.counter.set(data.rounds.length)
        }
      )
    }
  }
}
