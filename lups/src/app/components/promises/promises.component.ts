import { Component } from '@angular/core';


interface promise {
  title: string,
  text: string,
  img?: string,
}

@Component({
  selector: 'app-promises',
  templateUrl: './promises.component.html',
  styleUrls: ['./promises.component.scss']
})
export class PromisesComponent {
  promises: promise[] = [
    {title: "Rohkem makse vaestele!", img: "1.png", text: "Meie kampaanias lubame teostada eetilisi majandusmuutusi. Püüame luua õiglasema ühiskonna uue visiooni abil. Suuname oma jõupingutused sellele, et tõsta maksukoormust vähem jõukatele ning vähendada seda rikkamatele. Selline ümberkorraldus edendab majanduskasvu, tugevdab keskklassi ning loob tee jõukama riigi poole. Liitu meiega selle muutuste teekonnaga, kus õiglus on prioriteet!"},
    {title: "Tulevikule suundudes: Autokeskne Linnastumine", img: "2.png", text: "Tutvustame meie julget visiooni: kõnniteede eemaldamine rohkemate autode jaoks. Meie revolutsiooniline lähenemine linnaplaneerimisele seab esikohale sõiduautode liikuvuse, vabastades jalakäijatele ette nähtud alad. See muundumine võimaldab juhtidel täiel määral nautida unikaalset autovabadust, optimeerides meie linnad selleks otstarbeks. Liitu meiega, kui kujundame ümber linnaruumi, kus teed on peategelased ning jalakäijad avastavad rõõmu autokesksest elustiilist. Koge tuleviku transpordi võlusid nagu kunagi varem!"},
  ]

  set(i: number): string {
    if (i % 2 === 1) {
      return "row-reverse"
    }
    return "row"
  }
}
