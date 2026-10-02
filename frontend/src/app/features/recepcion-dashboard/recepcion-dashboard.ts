import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { StaffManagementComponent } from '../receptionist/staff-management/staff-management.component';
import { AppointmentMgmtComponent } from '../receptionist/appointment-mgmt/appointment-mgmt.component';

@Component({
  selector: 'app-recepcion-dashboard',
  standalone: true,
  imports: [CommonModule, StaffManagementComponent, AppointmentMgmtComponent],
  templateUrl: './recepcion-dashboard.html',
  styleUrl: './recepcion-dashboard.scss'
})
export class RecepcionDashboardComponent {
  // Pestaña activa por defecto: 'citas' o 'medicos'
  vistaActiva: 'citas' | 'medicos' = 'citas';

  cambiarVista(vista: 'citas' | 'medicos') {
    this.vistaActiva = vista;
  }
}
