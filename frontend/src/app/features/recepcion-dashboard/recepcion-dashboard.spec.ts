import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RecepcionDashboard } from './recepcion-dashboard';

describe('RecepcionDashboard', () => {
  let component: RecepcionDashboard;
  let fixture: ComponentFixture<RecepcionDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RecepcionDashboard],
    }).compileComponents();

    fixture = TestBed.createComponent(RecepcionDashboard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
