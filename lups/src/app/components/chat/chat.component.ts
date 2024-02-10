import {AfterViewChecked, Component, ElementRef, OnDestroy, OnInit, ViewChild} from '@angular/core';
import {MatDrawer, MatDrawerContainer, MatDrawerContent} from "@angular/material/sidenav";
import {MatFormField, MatLabel, MatSuffix} from "@angular/material/form-field";
import {MatIcon} from "@angular/material/icon";
import {MatIconButton, MatMiniFabButton} from "@angular/material/button";
import {MatInput} from "@angular/material/input";
import {MatOption} from "@angular/material/autocomplete";
import {MatProgressSpinner} from "@angular/material/progress-spinner";
import {MatSelect} from "@angular/material/select";
import {MatTooltip} from "@angular/material/tooltip";
import {NgClass, NgForOf, NgIf} from "@angular/common";
import {FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators} from "@angular/forms";
import {ChatData, ChatReceive, ChatSend, ChatService} from "../../services/chat.service";
import {ActivatedRoute, Router} from "@angular/router";
import {OAuthService} from "angular-oauth2-oidc";
import {UserInfoService} from "../../services/user-info.service";
import {BreakpointObserver} from "@angular/cdk/layout";
import {Subscription} from "rxjs";

export interface Message {
    message_id: number
    message_text: string
    message_owner: string
}

@Component({
    selector: 'app-chat',
    standalone: true,
    imports: [
        MatDrawer,
        MatDrawer,
        MatDrawerContainer,
        MatDrawerContainer,
        MatDrawerContent,
        MatDrawerContent,
        MatFormField,
        MatFormField,
        MatIcon,
        MatIcon,
        MatIconButton,
        MatIconButton,
        MatInput,
        MatInput,
        MatLabel,
        MatLabel,
        MatMiniFabButton,
        MatMiniFabButton,
        MatOption,
        MatOption,
        MatProgressSpinner,
        MatProgressSpinner,
        MatSelect,
        MatSelect,
        MatSuffix,
        MatSuffix,
        MatTooltip,
        MatTooltip,
        NgForOf,
        NgForOf,
        NgIf,
        NgIf,
        ReactiveFormsModule,
        ReactiveFormsModule,
        FormsModule,
        NgClass
    ],
    templateUrl: './chat.component.html',
    styleUrl: './chat.component.scss'
})
export class ChatComponent implements OnInit, OnDestroy, AfterViewChecked {
    textField: string;
    messages: Message[];
    chatId: number;
    chats: ChatData[]
    streamId: string;
    messagesLoaded: boolean;
    form: FormGroup;
    private streamSubscription: Subscription;

    languages = [
        // {display: 'Eesti', value: 'estonia'},
        {display: 'Inglise', value: 'english'},
    ];
    models = [
        {display: 'Väike', value: 'small'},
        // {display: 'Suur', value: 'large'},
    ];

    constructor(private chatService: ChatService,
                private router: Router,
                private oauthService: OAuthService,
                public userInfoService: UserInfoService,
                private observer: BreakpointObserver,
                private route: ActivatedRoute,
                private fb: FormBuilder
    ) {
        this.form = this.fb.group({
            language: ['english', Validators.required],
            model: ['small', Validators.required],
        });
    }

    onSubmit() {
        if (this.form.valid) {
            // Do something with the form data
            console.log(this.form.value);
        } else {
            // Handle invalid form
            console.log('Form is invalid');
        }
    }

    isSidenavOpen = false;
    isStreaming = false;

    toggleSidenav() {
        this.isSidenavOpen = !this.isSidenavOpen;
    }

    hasLoaded(): boolean {
        return this.messagesLoaded
    }

    ngOnDestroy() {
        if (this.streamSubscription) {
            this.streamSubscription.unsubscribe()
        }
    }

    ngOnInit() {
        if (!this.oauthService.hasValidIdToken()) {
            localStorage.setItem('originalUrl', window.location.pathname);
            this.oauthService.initLoginFlow('google');
            return
        }

        // load all user chats
        this.chatService.getChats().subscribe({
            next: (chats: ChatData[]) => {
                this.chats = chats

                // listen to url changes
                this.route.params.subscribe(params => {
                    console.log("params", params)
                    // no chat id
                    const chatId = params["id"]
                    if (!chatId) {
                        const lastChat = this.chats[this.chats.length - 1]
                        this.router.navigate(['/chat', lastChat.chat_id]);
                    } else {
                        this.loadComponent(chatId)
                    }
                })
            }
        })


    }

    loadComponent(id: number) {
        console.log("compobnent load", id)
        this.chatId = id
        this.messagesLoaded = false
        this.messages = []
        this.textField = ""
        this.streamId = ""
        this.isStreaming = false;

        // unsub if needed
        if (this.streamSubscription) {
            this.streamSubscription.unsubscribe()
        }

        // get all messages in a chat
        this.getAllMessagesInChat()
    }

    private getAllMessagesInChat(): void {
        this.chatService.getMessages(this.chatId).subscribe({
            next: (messages: Message[]) => {
                console.log(messages)
                this.messages = messages;
                this.messagesLoaded = true;
            },
            error: err => {
                console.log(err)
                // this.router.navigate([""])
            }
        })
    }

    ngAfterViewChecked() {
        this.scrollToBottom();
    }

    @ViewChild('scrollContainer') private scrollContainer: ElementRef | undefined;

    scrollToBottom(): void {
        const container = this.scrollContainer?.nativeElement
        if (!container) {
            return
        }
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth' // Add smooth scroll behavior
        });
    }

    private updateUserMessageId(id: number): void {
        // find last user message without id
        const msg = this.messages.find(o => o.message_owner === "user" && o.message_id === -1)
        if (msg) {
            msg.message_id = id
        }
    }

    private updateModelMessage(chatReceive: ChatReceive): void {
        this.messages[this.messages.length - 1].message_text = chatReceive.text

        // need to use for loop or else the ui is messed up
        let msg: Message | null = null
        for (let i = this.messages.length - 1; i >= 0; i--) {
            const message = this.messages[i]
            if (message.message_id === -1 && message.message_owner === "model") {
                msg = message
                break
            }
        }
        if (!msg) {
            msg = {
                message_id: chatReceive.id,
                message_text: chatReceive.text,
                message_owner: "model"
            }
            this.messages.push(msg)
        }
        if (chatReceive.type === "part") {
            msg.message_text = chatReceive.text
        } else if (chatReceive.type === "end") {
            msg.message_text = chatReceive.text
            msg.message_id = chatReceive.id
            this.isStreaming = false;
        }
    }


    send() {
        this.isStreaming = true;
        const message: ChatSend = {
            type: "message",
            ai_model_type: this.form.value["model"],
            language_type: this.form.value["language"],
            message_id: -1,
            message_text: this.textField,
        }
        this.messages.push({
            message_id: -1,
            message_owner: "user",
            message_text: this.textField
        })
        this.messages.push({
            message_id: -1,
            message_owner: "model",
            message_text: "Loading..."
        })

        this.chatService.postMessage(this.chatId, message).subscribe({
            next: chatSendRespond => {
                console.log("stream id", chatSendRespond)
                this.streamId = chatSendRespond.stream_id
                this.updateUserMessageId(chatSendRespond.message_id)
                this.streamSubscription = this.chatService.getStreamMessages(this.streamId).subscribe({
                    next: chatReceive => {
                        this.updateModelMessage(chatReceive)
                    }
                })
            }
        })
        this.textField = ""
    }

    cancel() {
        this.chatService.deleteStream(this.streamId).subscribe(
            () => {
                this.streamId = ""
            }
        )
    }

    createNew() {
        this.messagesLoaded = false
        this.chatService.newChat().subscribe({
            next: (chatData: ChatData) => {
                this.chats.push(chatData)
                this.router.navigate(["chat", chatData.chat_id])
            }
        })
    }

    toggleEdit(chat: ChatData) {
        if (chat.editing) {
            this.chatService.editChatTitle(chat.chat_id, chat.title).subscribe()
        }
        chat.editing = !chat.editing
    }

    onTitleChange(event: Event, chat: ChatData): void {
        const inputValue = (event.target as HTMLInputElement).value;
        // Update the title of the item
        chat.title = inputValue;
    }

    selectChat(id: number) {
        this.router.navigate(["chat", id])
    }
}
