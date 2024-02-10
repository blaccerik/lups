import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PromisesComponent } from './promises.component';

describe('PromisesComponent', () => {
  let component: PromisesComponent;
  let fixture: ComponentFixture<PromisesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PromisesComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(PromisesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
