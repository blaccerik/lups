import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NotLoggedInPopupComponent } from './not-logged-in-popup.component';

describe('NotLoggedInPopupComponent', () => {
  let component: NotLoggedInPopupComponent;
  let fixture: ComponentFixture<NotLoggedInPopupComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [NotLoggedInPopupComponent]
    });
    fixture = TestBed.createComponent(NotLoggedInPopupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
