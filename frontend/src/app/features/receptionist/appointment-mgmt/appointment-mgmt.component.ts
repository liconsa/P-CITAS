import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-appointment-mgmt',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './appointment-mgmt.component.html',
  styleUrl: 'appointment-mgmt.component.scss'
})
export class AppointmentMgmtComponent implements OnInit {
  citas: any[] = [];
  mensaje: string = '';
  cargando: boolean = false;

  constructor(
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cargarCitas();
  }

  cargarCitas() {
    this.cargando = true;
    this.api.get('receptionist/appointments-all').subscribe({
      next: (data: any) => {
        this.citas = data || [];
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar citas:', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  confirmarCita(citaId: number) {
    this.api.post(`receptionist/appointments/${citaId}/confirmar`, {}).subscribe({
      next: () => {
        this.mensaje = '✅ Cita confirmada exitosamente.';
        this.cargarCitas();
        this.cdr.detectChanges();
      },
      error: () => {
        this.mensaje = '❌ Error al confirmar la cita.';
        this.cdr.detectChanges();
      }
    });
  }

  cancelarCita(citaId: number) {
    this.api.post(`receptionist/appointments/${citaId}/cancelar`, {}).subscribe({
      next: () => {
        this.mensaje = '✅ Cita cancelada correctamente.';
        this.cargarCitas();
        this.cdr.detectChanges();
      },
      error: () => {
        this.mensaje = '❌ Error al cancelar la cita.';
        this.cdr.detectChanges();
      }
    });
  }
}
