import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminBoardComponent } from './admin-board.component';

describe('LivegameComponent', () => {
  let component: AdminBoardComponent;
  let fixture: ComponentFixture<AdminBoardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminBoardComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdminBoardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
