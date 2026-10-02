import { Routes } from '@angular/router';
import { RoleGuard } from './core/guards/role.guard';

// Componentes de Autenticación
import { LoginComponent } from './features/auth/login/login.component';

// Componentes del Paciente (¡Incluyendo el nuevo Dashboard!)
import { DashboardComponent as PatientDashboardComponent } from './features/patient/dashboard/dashboard.component';
import { ScheduleComponent } from './features/patient/schedule/schedule.component';
import { MyAppointmentsComponent } from './features/patient/my-appointments/my-appointments.component';
import { MyHistoryComponent} from './features/medical-history/medical-history.component';
// Otros Roles
import { DashboardComponent as AdminDashboardComponent } from './features/admin/dashboard/dashboard.component';
import { AgendaComponent } from './features/doctor/agenda/agenda.component';
import { PrescriptionsComponent } from './features/doctor/prescriptions/prescriptions.component';
import { StaffManagementComponent } from './features/receptionist/staff-management/staff-management.component';
import { AppointmentMgmtComponent } from './features/receptionist/appointment-mgmt/appointment-mgmt.component';

export const routes: Routes = [
  { path: '', redirectTo: 'auth/login', pathMatch: 'full' },
  { path: 'auth/login', component: LoginComponent },

  // Rutas del Administrador
  {
    path: 'admin',
    component: AdminDashboardComponent,
    canActivate: [RoleGuard],
    data: { rolesEsperados: ['admin'] }
  },

  // Rutas del Paciente (¡ARREGLADAS!)
  {
    path: 'patient',
    canActivate: [RoleGuard],
    data: { rolesEsperados: ['paciente', 'admin'] },
    children: [
      // Si entran a /patient a secas, ahora los manda al nuevo Dashboard de bienvenida
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: PatientDashboardComponent },
      { path: 'schedule', component: ScheduleComponent },
      { path: 'appointments', component: MyAppointmentsComponent },
      { path: 'history', component: MyHistoryComponent }
    ]
  },

  // Rutas del Médico
  {
    path: 'doctor',
    canActivate: [RoleGuard],
    data: { rolesEsperados: ['medico', 'admin'] },
    children: [
      { path: '', redirectTo: 'agenda', pathMatch: 'full' },
      { path: 'agenda', component: AgendaComponent },
      { path: 'prescriptions', component: PrescriptionsComponent }
    ]
  },

  // Rutas del Recepcionista
  {
    path: 'receptionist',
    canActivate: [RoleGuard],
    data: { rolesEsperados: ['recepcionista', 'admin'] },
    children: [
      { path: '', redirectTo: 'appointments', pathMatch: 'full' },
      { path: 'appointments', component: AppointmentMgmtComponent },
      { path: 'staff', component: StaffManagementComponent }
    ]
  }
];
