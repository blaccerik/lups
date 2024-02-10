import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SingleNewsComponent } from './single-news.component';

describe('SingleNewsComponent', () => {
  let component: SingleNewsComponent;
  let fixture: ComponentFixture<SingleNewsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [SingleNewsComponent]
    });
    fixture = TestBed.createComponent(SingleNewsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
