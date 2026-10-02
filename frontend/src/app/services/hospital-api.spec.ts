import { TestBed } from '@angular/core/testing';
import { HospitalApi } from './hospital-api';

describe('HospitalApi', () => {
  let service: HospitalApi;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(HospitalApi);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
