import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateNewsComponent } from './create-news.component';

describe('NewsComponent', () => {
  let component: CreateNewsComponent;
  let fixture: ComponentFixture<CreateNewsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CreateNewsComponent]
    });
    fixture = TestBed.createComponent(CreateNewsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
