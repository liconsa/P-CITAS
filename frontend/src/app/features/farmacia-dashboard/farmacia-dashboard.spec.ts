import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FarmaciaDashboard } from './farmacia-dashboard';

describe('FarmaciaDashboard', () => {
  let component: FarmaciaDashboard;
  let fixture: ComponentFixture<FarmaciaDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FarmaciaDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(FarmaciaDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
