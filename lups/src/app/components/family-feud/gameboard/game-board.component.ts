import {Component, computed, inject, OnDestroy, OnInit, signal} from '@angular/core';
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {NgForOf, NgIf} from "@angular/common";
import {FamilyfeudService, LiveGame} from "../../../services/familyfeud.service";
import {GamebannerComponent} from "../gamebanner/gamebanner.component";
import {ActivatedRoute, Router, RouterLink} from "@angular/router";
import {Subscription} from "rxjs";


interface AnswerBox {
  text: string
  revealed: boolean
  number: number
  points: number
}

@Component({
  selector: 'app-gameboard',
  standalone: true,
  imports: [
    MatProgressSpinner,
    NgIf,
    GamebannerComponent,
    RouterLink,
    NgForOf
  ],
  templateUrl: './game-board.component.html',
  styleUrl: './game-board.component.scss'
})
export class GameBoardComponent implements OnInit, OnDestroy {
  private familyfeudService = inject(FamilyfeudService)
  private route = inject(ActivatedRoute)
  private router = inject(Router)

  game = signal<LiveGame>({
    strikes: -1,
    question: "",
    answers: [],
    type: "",
    number: -1
  })
  answers = signal<AnswerBox[]>([])
  loading = signal(true)

  points = signal(0)
  strikes = computed<number[]>(() => new Array(this.game().strikes))
  // strikes = signal([1,2,3])
  showStrike= true;
  familyfeudService$: Subscription

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const code = params["id"]
      this.familyfeudService$ = this.familyfeudService.connect(code, "").subscribe(
        data => {
          console.log("board", data)
          if (data.type === "error") {
            this.router.navigate(["/familyfeud"])
            return
          }

          if (data.strikes !== 0) {
            this.showStrike = true
            setTimeout(() => {
              this.showStrike = false;
            }, 1000);
          }

          this.game.set(data)
          this.points.set(data.answers
            .filter(answer => answer.revealed)
            .reduce((sum, answer) => sum + answer.points, 0)
          )
          const answerBoxes = []
          for (let i = 0; i < 10; i++) {
            let box: AnswerBox
            if (i < data.answers.length) {
              const answer = data.answers[i]
              box = {
                text: answer.text,
                revealed: answer.revealed,
                // revealed: i % 2 === 0,
                number: i + 1,
                points: answer.points
              }
            } else {
              box = {
                text: "",
                revealed: false,
                number: -1,
                points: 0
              }
            }
            answerBoxes.push(box)
          }
          this.answers.set(answerBoxes)
        }
      )
    });
  }

  ngOnDestroy(): void {
    this.familyfeudService.disconnect()
    if (this.familyfeudService$) {
      this.familyfeudService$.unsubscribe()
    }
  }
}
