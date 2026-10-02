import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-my-appointments',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './my-appointments.component.html',
  styleUrl: './my-appointments.component.scss'
})
export class MyAppointmentsComponent implements OnInit {
  citasPendientes: any[] = [];
  citasHistorial: any[] = [];
  mensaje: string = '';

  constructor(
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cargarCitas();
  }

  cargarCitas() {
    this.api.get<any[]>('patient/citas').subscribe({
      next: (res) => {
        // Tabla 1: Citas activas o pendientes
        this.citasPendientes = res.filter(cita => cita.estado === 'PENDIENTE');

        // Tabla 2: El resto (canceladas, completadas, pasadas, etc.)
        this.citasHistorial = res.filter(cita => cita.estado !== 'PENDIENTE');

        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar citas', err);
        this.cdr.detectChanges();
      }
    });
  }

  cancelarCita(id: number) {
    if (confirm('¿Estás seguro de que deseas cancelar esta cita?')) {
      this.api.post(`patient/citas/${id}/cancelar`, {}).subscribe({
        next: (res: any) => {
          this.mensaje = `✅ Cita cancelada con éxito. Reembolso autorizado: $${res.reembolso_calculado}`;
          this.cargarCitas();
          this.cdr.detectChanges();
        },
        error: () => {
          this.mensaje = '❌ Error al intentar cancelar la cita.';
          this.cdr.detectChanges();
        }
      });
    }
  }
}
