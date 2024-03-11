import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GamebannerComponent } from './gamebanner.component';

describe('GamebannerComponent', () => {
  let component: GamebannerComponent;
  let fixture: ComponentFixture<GamebannerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GamebannerComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(GamebannerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
