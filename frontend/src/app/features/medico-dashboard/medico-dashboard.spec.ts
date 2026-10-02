import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MedicoDashboard } from './medico-dashboard';

describe('MedicoDashboard', () => {
  let component: MedicoDashboard;
  let fixture: ComponentFixture<MedicoDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MedicoDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(MedicoDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
