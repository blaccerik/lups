import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PonyComponent } from './pony.component';

describe('PonyComponent', () => {
  let component: PonyComponent;
  let fixture: ComponentFixture<PonyComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PonyComponent]
    });
    fixture = TestBed.createComponent(PonyComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
