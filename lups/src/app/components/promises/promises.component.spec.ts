import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PromisesComponent } from './promises.component';

describe('PromisesComponent', () => {
  let component: PromisesComponent;
  let fixture: ComponentFixture<PromisesComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [PromisesComponent]
    });
    fixture = TestBed.createComponent(PromisesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
