import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FamilyFeudComponent } from './family-feud.component';

describe('FamilyFeudComponent', () => {
  let component: FamilyFeudComponent;
  let fixture: ComponentFixture<FamilyFeudComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FamilyFeudComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FamilyFeudComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
