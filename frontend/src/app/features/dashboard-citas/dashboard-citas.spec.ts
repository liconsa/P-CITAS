import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DashboardCitas } from './dashboard-citas';

describe('DashboardCitas', () => {
  let component: DashboardCitas;
  let fixture: ComponentFixture<DashboardCitas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [DashboardCitas],
    }).compileComponents();

    fixture = TestBed.createComponent(DashboardCitas);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
