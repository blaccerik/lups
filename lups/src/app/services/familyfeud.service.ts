import {inject, Injectable, signal, WritableSignal} from '@angular/core';
import {retry, Subject} from "rxjs";
import {HttpClient} from "@angular/common/http";
import {OAuthService} from "angular-oauth2-oidc";
import {environment} from "../../environments/environment";
import {webSocket} from "rxjs/webSocket";
import {toSignal} from "@angular/core/rxjs-interop";
import {PixelResponse} from "./place.service";

export interface Answer {
  text: string
  points: number
  revealed?: boolean
  editing?: boolean
}

export interface GameData {
  rounds: GameRound[]
  started: boolean
  code: string
  auth: string
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
  stared: boolean
}

export interface LiveGameAnswer {
  text: string
  points: number
  revealed: boolean
}

export interface LiveGame {
  type: string
  answers: LiveGameAnswer[]
  number: number
  question: string
  strikes: number
}

@Injectable({
  providedIn: 'root'
})
export class FamilyfeudService {
  private url = "api/familyfeud"
  private http = inject(HttpClient)
  private oauthService = inject(OAuthService)
  private subject: any;
  private roundSubject = new Subject<LiveGame>();

  connect(code: string, auth: string) {
    if (this.subject) {
      this.subject.unsubscribe()
    }
    this.subject = webSocket(`${environment.wsUrl}/api/familyfeud/ws/${code}?auth=${auth}`);

    // get websocket
    this.subject.pipe(retry({delay: 1000})).subscribe(
      (data: LiveGame) => {
        this.roundSubject.next(data)
      })
    return this.roundSubject.asObservable();
  }

  disconnect() {
    if (this.subject) {
      this.subject.unsubscribe()
    }
  }

  sendData(data: LiveGame) {
    if (this.subject) {
      this.subject.next(data)
    }
  }

  getGames() {
    return this.http.get<Game[]>(this.url + "/games")
  }

  createGame() {
    return this.http.post<Game>(this.url + "/create", {})
  }

  getGameByCode(code: string) {
    return this.http.get<GameData>(this.url + "/games/" + code)
  }

  postGameByCode(code: string, gameRounds: GameRound[]) {
    return this.http.post<GameData>(this.url + "/games/" + code, gameRounds)
  }

  setGameStatus(code: string, started: boolean) {
    return this.http.post<Game>(this.url + "/games/" + code + "/status", {started: started})
  }
}
