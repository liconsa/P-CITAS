import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-my-history',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-history.component.html'
})
export class MyHistoryComponent implements OnInit {
  historialCitas: any[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.cargarHistorial();
  }

  cargarHistorial() {
    // Un paciente puede consultar su historial de citas.[cite: 1]
    this.api.get<any[]>('patient/citas').subscribe(
      res => this.historialCitas = res
    );
  }
}
