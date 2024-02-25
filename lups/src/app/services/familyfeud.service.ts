import {inject, Injectable, signal, WritableSignal} from '@angular/core';
import {retry} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {OAuthService} from "angular-oauth2-oidc";
import {environment} from "../../environments/environment";
import {webSocket} from "rxjs/webSocket";
import {toSignal} from "@angular/core/rxjs-interop";

export interface Answer {
  text: string
  points: number
  revealed?: boolean
  editing?: boolean
}

interface GameData {
  current: number
  total: number
  question: string
  answers: Answer[]
}

export interface GameRound {
  answers: Answer[]
  question: string
  round_number: number
  editing?: boolean
}

export interface Game {
  code: string
  auth: string
}

@Injectable({
  providedIn: 'root'
})
export class FamilyfeudService {
  private url = "api/familyfeud"
  private http = inject(HttpClient)
  private oauthService = inject(OAuthService)
  private subject: any;
  gameData: WritableSignal<GameData | null> = signal(null);

  connect(code: string) {
    console.log(environment.wsUrl)
    this.gameData.set(null)
    if (this.subject) {
      this.subject.unsubscribe()
    }
    if (this.oauthService.hasValidIdToken()) {
      const token = this.oauthService.getIdToken();
      this.subject = webSocket(`${environment.wsUrl}/api/familyfeud/ws/${code}?auth=${token}`);
    } else {
      this.subject = webSocket(`${environment.wsUrl}/api/familyfeud/ws/${code}`);
    }

    // get websocket
    this.subject.pipe(retry({delay: 1000})).subscribe(
      (data: GameData) => {
        console.log(data)
        this.gameData.set(data)
      })
  }

  disconnect() {
    if (this.subject) {
      this.subject.unsubscribe()
    }
  }

  getGames() {
    return this.http.get<Game[]>(this.url + "/games")
  }

  createGame() {
    return this.http.post<Game>(this.url + "/create", {})
  }

  getGameByCode(code: string) {
    return this.http.get<GameRound[]>(this.url + "/games/" + code)
  }

  postGameByCode(code: string, gameRounds: GameRound[]) {

    return this.http.post<GameRound[]>(this.url + "/games/" + code, gameRounds)
  }
}
