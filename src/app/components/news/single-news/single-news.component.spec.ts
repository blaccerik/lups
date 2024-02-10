import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SingleNewsComponent } from './single-news.component';

describe('SingleNewsComponent', () => {
  let component: SingleNewsComponent;
  let fixture: ComponentFixture<SingleNewsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SingleNewsComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(SingleNewsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
