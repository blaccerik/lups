import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdminboardComponent } from './adminboard.component';

describe('AdminboardComponent', () => {
  let component: AdminboardComponent;
  let fixture: ComponentFixture<AdminboardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdminboardComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(AdminboardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
