import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-staff-management',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './staff-management.component.html'
})
export class StaffManagementComponent implements OnInit {
  doctores: any[] = [];
  mensaje: string = '';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.cargarDoctores();
  }

  cargarDoctores() {
    this.api.get<any[]>('admin/usuarios?rol=medico').subscribe(
      res => this.doctores = res.filter(user => user.rol === 'medico')
    );
  }

  cambiarEstado(id: number, estadoActual: boolean) {
    const nuevoEstado = !estadoActual;
    // El recepcionista podrá realizar operaciones de alta y baja del personal médico.[cite: 1]
    this.api.put(`receptionist/doctores/${id}/estado?activo=${nuevoEstado}`, {}).subscribe({
      next: () => {
        this.mensaje = `Estado del médico actualizado correctamente.`;
        this.cargarDoctores(); // Refrescar la tabla
      },
      error: () => this.mensaje = 'Ocurrió un error al actualizar el estado.'
    });
  }
}
