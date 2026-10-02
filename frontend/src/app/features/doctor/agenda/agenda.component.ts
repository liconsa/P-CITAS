import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-agenda',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './agenda.component.html'
})
export class AgendaComponent implements OnInit {
  citas: any[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.cargarAgenda();
  }

  cargarAgenda() {
    // El médico podrá visualizar sus citas programadas.[cite: 1]
    this.api.get<any[]>('doctor/agenda').subscribe(
      res => this.citas = res
    );
  }
}
