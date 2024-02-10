import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MiniNewsComponent } from './mini-news.component';

describe('MiniNewsComponent', () => {
  let component: MiniNewsComponent;
  let fixture: ComponentFixture<MiniNewsComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MiniNewsComponent]
    });
    fixture = TestBed.createComponent(MiniNewsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
