import {Component, inject, Input, OnDestroy, OnInit} from '@angular/core';
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {NgIf} from "@angular/common";
import {ChatService} from "../../../services/chat.service";
import {FamilyfeudService} from "../../../services/familyfeud.service";
import {GamebannerComponent} from "../gamebanner/gamebanner.component";
import {ActivatedRoute, RouterLink} from "@angular/router";
import {switchMap} from "rxjs";

@Component({
  selector: 'app-gameboard',
  standalone: true,
  imports: [
    MatProgressSpinner,
    NgIf,
    GamebannerComponent,
    RouterLink
  ],
  templateUrl: './gameboard.component.html',
  styleUrl: './gameboard.component.scss'
})
export class GameboardComponent implements OnInit, OnDestroy {
  private familyfeudService = inject(FamilyfeudService)
  private route = inject(ActivatedRoute)
  gameData = this.familyfeudService.gameData
  ngOnInit(): void {
    this.route.params.subscribe(params => {
      const code = params["id"]
      this.familyfeudService.connect(code)
    });
  }

  ngOnDestroy(): void {
    this.familyfeudService.disconnect()
  }
}
