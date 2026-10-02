import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-appointment-mgmt',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './appointment-mgmt.component.html'
})
export class AppointmentMgmtComponent implements OnInit {
  citas: any[] = [];
  mensaje: string = '';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.cargarTodasLasCitas();
  }

  cargarTodasLasCitas() {
    // Se asume un endpoint general para que recepción vea las citas
    this.api.get<any[]>('admin/citas').subscribe(
      res => this.citas = res
    );
  }

  cambiarEstadoCita(id: number, nuevoEstado: string) {
    // El recepcionista podrá intervenir en el proceso de confirmación o cancelación de citas.
    this.api.put(`receptionist/citas/${id}/estado?nuevo_estado=${nuevoEstado}`, {}).subscribe({
      next: () => {
        this.mensaje = `Cita ${nuevoEstado.toLowerCase()} exitosamente.`;
        this.cargarTodasLasCitas();
      },
      error: () => this.mensaje = 'Error al actualizar el estado de la cita.'
    });
  }
}
