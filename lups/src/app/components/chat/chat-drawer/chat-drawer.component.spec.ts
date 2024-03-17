import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatDrawerComponent } from './chat-drawer.component';

describe('ChatDrawerComponent', () => {
  let component: ChatDrawerComponent;
  let fixture: ComponentFixture<ChatDrawerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatDrawerComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ChatDrawerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
