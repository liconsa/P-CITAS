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
        this.citasPendientes = res.filter(cita =>
          cita.estado === 'PENDIENTE' || cita.estado === 'PAGADA' || cita.estado === 'PAGADO'
        );
        this.citasHistorial = res.filter(cita =>
          cita.estado !== 'PENDIENTE' && cita.estado !== 'PAGADA' && cita.estado !== 'PAGADO'
        );
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar citas', err);
        this.cdr.detectChanges();
      }
    });
  }

  // Pago directo automático sin prompts molestos para evitar que se trabe
  pagarCita(cita: any) {
    const folioSimulado = `FOL-${Date.now().toString().slice(-6)}`;

    this.api.post(`patient/citas/${cita.id}/pagar`, { folio_pago: folioSimulado }).subscribe({
      next: (res: any) => {
        this.mensaje = `✅ ¡Cita pagada con éxito! Folio asignado: ${res.folio_pago}`;
        this.cargarCitas();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.mensaje = '❌ Error al procesar el pago.';
        this.cdr.detectChanges();
      }
    });
  }

  cancelarCita(id: number) {
    if (confirm('¿Estás seguro de cancelar esta cita? Se aplicará el reembolso correspondiente.')) {
      this.api.post(`patient/citas/${id}/cancelar`, {}).subscribe({
        next: (res: any) => {
          this.mensaje = `✅ Cita cancelada con éxito. Reembolso: $${res.reembolso_calculado}`;
          this.cargarCitas();
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.mensaje = '❌ Error al cancelar la cita.';
          this.cdr.detectChanges();
        }
      });
    }
  }
}
