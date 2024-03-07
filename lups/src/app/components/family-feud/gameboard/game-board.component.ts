import {Component, inject, Input, OnDestroy, OnInit, signal} from '@angular/core';
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {NgIf} from "@angular/common";
import {ChatService} from "../../../services/chat.service";
import {FamilyfeudService, GameData, GameRound, LiveGame} from "../../../services/familyfeud.service";
import {GamebannerComponent} from "../gamebanner/gamebanner.component";
import {ActivatedRoute, Router, RouterLink} from "@angular/router";
import {Subscription, switchMap} from "rxjs";

@Component({
  selector: 'app-gameboard',
  standalone: true,
  imports: [
    MatProgressSpinner,
    NgIf,
    GamebannerComponent,
    RouterLink
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
  loading = signal(true)

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
          this.game.set(data)
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
