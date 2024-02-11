import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GamecodeComponent } from './gamecode.component';

describe('GamecodeComponent', () => {
  let component: GamecodeComponent;
  let fixture: ComponentFixture<GamecodeComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GamecodeComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(GamecodeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
