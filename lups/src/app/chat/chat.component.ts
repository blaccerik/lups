import {Component, ElementRef, ViewChild} from '@angular/core';
import {ChatResponse, ChatService} from "../services/chat.service";

interface Message {
  text: string;
  isUser: boolean;
  isLoading: boolean;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent {

  textFieldValue: string = "";
  titleText: string;
  titleTextIndex: number = 0;
  imgPath: string = "assets/tonu/tonu.png"
  titleTexts = [
    "'Maailm pole valmis tõde kuulama' - Tõnu",
    "'Maailm väljas, muusika sees' - Tõnu",
    "'Ma peksan kõik läbi' - Tõnu"
  ]

  messages: Message[] = [];
  @ViewChild('chatContainer') private chatContainer: ElementRef;

  startTitleTextRotation() {
    this.titleText = this.titleTexts[0]

    setInterval(() => {
      this.titleTextIndex += 1;
      if (this.titleTextIndex >= this.titleTexts.length) {
        this.titleTextIndex = 0;
      }
      this.titleText = this.titleTexts[this.titleTextIndex];
    }, 5000);
  }

  constructor(private chatService: ChatService) {
    const msg: Message = {
      text: "Tere! Mina olen Tõnu ja olen valmis vastama sinu küsimustele.",
      isUser: false,
      isLoading: false
    };
    this.messages.push(msg)
    this.startTitleTextRotation()
  }

  submit() {
    const userMessage: Message = {
      text: this.textFieldValue,
      isUser: true,
      isLoading: false
    };
    this.messages.push(userMessage);

    const loadingMessage: Message = {
      text: "",
      isUser: false,
      isLoading: true
    };
    this.messages.push(loadingMessage);

    this.sendPostRequest(this.textFieldValue);
    this.textFieldValue = ""; // Clear the input field

    // Scroll to the latest question
    setTimeout(() => {
      this.scrollToBottom();
    }, 0);
  }

  sendPostRequest(msg: string) {
    this.chatService.sendChatMessage(msg).subscribe({
      next: (response: ChatResponse) => {
        const loadingMessageIndex = this.messages.findIndex(msg => msg.isLoading);
        if (loadingMessageIndex > -1) {
          this.messages.splice(loadingMessageIndex, 1);
        }

        const appMessage: Message = {
          text: response.output_text_ee,
          isUser: false,
          isLoading: false
        };
        this.messages.push(appMessage);

      },
      error: (error: any) => {
        console.log(error);
      }
    });
  }

  scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.lastElementChild?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    } catch (err) {
      console.log(err);
    }
  }
}
