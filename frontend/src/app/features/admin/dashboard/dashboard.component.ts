import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, FormsModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit {
  pestanaActiva: 'jornadas' | 'usuarios' = 'jornadas';

  // Médicos y Jornadas
  medicos: any[] = [];
  jornadas: any[] = [];
  cargandoJornadas: boolean = false;
  filtroMedicoId: string = '';
  filtroFecha: string = '';

  // Formulario de Postulación de Jornadas (Batch)
  jornadaForm: FormGroup;
  horasDisponibles: string[] = [
    '08:00', '09:00', '10:00', '11:00', '12:00',
    '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'
  ];
  horasSeleccionadas: string[] = [];
  horaPersonalizada: string = '';

  // Usuarios
  usuarios: any[] = [];
  cargandoUsuarios: boolean = false;
  usuarioForm: FormGroup;
  filtroRol: string = 'todos';
  filtroBusquedaUsuario: string = '';

  // Mensajes de retroalimentación
  mensajeExito: string = '';
  mensajeError: string = '';

  constructor(
    private api: ApiService,
    private auth: AuthService,
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef
  ) {
    // Formulario para crear usuario
    this.usuarioForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      correo: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(4)]],
      rol: ['medico', Validators.required],
      especialidad: ['Medicina General']
    });

    // Formulario para asignar jornada / postulación
    this.jornadaForm = this.fb.group({
      medico_id: ['', Validators.required],
      fecha: ['', Validators.required],
      duracion_minutos: [60, [Validators.required, Validators.min(15), Validators.max(120)]]
    });
  }

  ngOnInit() {
    this.cargarMedicos();
    this.cargarJornadas();
    this.cargarUsuarios();
  }

  cambiarPestana(pestana: 'jornadas' | 'usuarios') {
    this.pestanaActiva = pestana;
    this.limpiarMensajes();
  }

  // ==========================================
  // GESTIÓN DE MÉDICOS Y JORNADAS (POSTULACIONES)
  // ==========================================

  cargarMedicos() {
    this.api.get<any[]>('admin/medicos').subscribe({
      next: (data) => {
        this.medicos = data;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Error al cargar médicos:', err)
    });
  }

  cargarJornadas() {
    this.cargandoJornadas = true;
    let endpoint = 'admin/jornadas';
    const params: string[] = [];
    if (this.filtroMedicoId) params.push(`medico_id=${this.filtroMedicoId}`);
    if (this.filtroFecha) params.push(`fecha=${this.filtroFecha}`);
    if (params.length > 0) endpoint += `?${params.join('&')}`;

    this.api.get<any[]>(endpoint).subscribe({
      next: (data) => {
        this.jornadas = data;
        this.cargandoJornadas = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar jornadas:', err);
        this.cargandoJornadas = false;
        this.cdr.detectChanges();
      }
    });
  }

  toggleHora(hora: string) {
    const index = this.horasSeleccionadas.indexOf(hora);
    if (index > -1) {
      this.horasSeleccionadas.splice(index, 1);
    } else {
      this.horasSeleccionadas.push(hora);
      this.horasSeleccionadas.sort();
    }
  }

  estaHoraSeleccionada(hora: string): boolean {
    return this.horasSeleccionadas.includes(hora);
  }

  seleccionarTodasLasHoras() {
    this.horasSeleccionadas = [...this.horasDisponibles];
  }

  limpiarHoras() {
    this.horasSeleccionadas = [];
  }

  agregarHoraPersonalizada() {
    if (!this.horaPersonalizada) return;
    if (!this.horasDisponibles.includes(this.horaPersonalizada)) {
      this.horasDisponibles.push(this.horaPersonalizada);
      this.horasDisponibles.sort();
    }
    if (!this.horasSeleccionadas.includes(this.horaPersonalizada)) {
      this.horasSeleccionadas.push(this.horaPersonalizada);
      this.horasSeleccionadas.sort();
    }
    this.horaPersonalizada = '';
  }

  crearJornadas() {
    this.limpiarMensajes();

    if (this.jornadaForm.invalid) {
      this.mensajeError = 'Por favor completa todos los campos del formulario de postulación.';
      return;
    }

    if (this.horasSeleccionadas.length === 0) {
      this.mensajeError = 'Debes seleccionar al menos un horario para la jornada.';
      return;
    }

    const payload = {
      medico_id: Number(this.jornadaForm.value.medico_id),
      fecha: this.jornadaForm.value.fecha,
      horas: this.horasSeleccionadas,
      duracion_minutos: Number(this.jornadaForm.value.duracion_minutos)
    };

    this.api.post<any[]>('admin/jornadas/batch', payload).subscribe({
      next: (creadas: any[]) => {
        const medicoSeleccionado = this.medicos.find(m => m.id === payload.medico_id);
        const nombreDoc = medicoSeleccionado ? medicoSeleccionado.nombre : 'médico';
        this.mensajeExito = `¡Se publicaron exitosamente ${creadas.length} horarios de jornada para el ${nombreDoc} en la fecha ${payload.fecha}!`;
        this.horasSeleccionadas = [];
        this.cargarJornadas();
      },
      error: (err) => {
        console.error('Error al crear jornadas:', err);
        this.mensajeError = err.error?.detail || 'Error al asignar las jornadas laborales.';
      }
    });
  }

  eliminarJornada(jornada: any) {
    if (!confirm(`¿Eliminar la jornada de ${jornada.medico_nombre || 'médico'} a las ${this.formatearHora(jornada.fecha_hora)}?`)) {
      return;
    }

    this.api.delete(`admin/jornadas/${jornada.id}`).subscribe({
      next: () => {
        this.mensajeExito = 'Jornada eliminada correctamente.';
        this.cargarJornadas();
      },
      error: (err) => {
        this.mensajeError = err.error?.detail || 'No se pudo eliminar la jornada.';
      }
    });
  }

  // ==========================================
  // GESTIÓN DE USUARIOS
  // ==========================================

  cargarUsuarios() {
    this.cargandoUsuarios = true;
    this.api.get<any[]>('admin/usuarios').subscribe({
      next: (data) => {
        this.usuarios = data;
        this.cargandoUsuarios = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar usuarios:', err);
        this.cargandoUsuarios = false;
        this.cdr.detectChanges();
      }
    });
  }

  crearUsuario() {
    this.limpiarMensajes();

    if (this.usuarioForm.invalid) {
      this.mensajeError = 'Por favor completa correctamente los datos del usuario.';
      return;
    }

    const formValue = this.usuarioForm.value;
    const rol = formValue.rol;

    this.api.post<any>(`admin/usuarios?rol=${rol}`, formValue).subscribe({
      next: (nuevo: any) => {
        this.mensajeExito = `Usuario ${nuevo.nombre} (${rol}) creado exitosamente.`;
        this.usuarioForm.reset({
          rol: 'medico',
          especialidad: 'Medicina General'
        });
        this.cargarUsuarios();
        this.cargarMedicos();
      },
      error: (err) => {
        console.error('Error al crear usuario:', err);
        this.mensajeError = err.error?.detail || 'Error al registrar el usuario en el sistema.';
      }
    });
  }

  eliminarUsuario(u: any) {
    if (!confirm(`¿Estás seguro de eliminar al usuario ${u.nombre} (${u.rol})?`)) {
      return;
    }

    this.api.delete(`admin/usuarios/${u.id}`).subscribe({
      next: () => {
        this.mensajeExito = `Usuario ${u.nombre} eliminado del sistema.`;
        this.cargarUsuarios();
        this.cargarMedicos();
      },
      error: (err) => {
        this.mensajeError = err.error?.detail || 'No se pudo eliminar el usuario.';
      }
    });
  }

  get usuariosFiltrados(): any[] {
    return this.usuarios.filter(u => {
      const coincideRol = this.filtroRol === 'todos' || u.rol.toLowerCase() === this.filtroRol.toLowerCase();
      const coincideTexto = !this.filtroBusquedaUsuario ||
        u.nombre.toLowerCase().includes(this.filtroBusquedaUsuario.toLowerCase()) ||
        u.correo.toLowerCase().includes(this.filtroBusquedaUsuario.toLowerCase()) ||
        (u.especialidad && u.especialidad.toLowerCase().includes(this.filtroBusquedaUsuario.toLowerCase()));
      return coincideRol && coincideTexto;
    });
  }

  // ==========================================
  // ESTADÍSTICAS RÁPIDAS
  // ==========================================

  get totalMedicos(): number {
    return this.usuarios.filter(u => u.rol.toLowerCase() === 'medico').length;
  }

  get totalPacientes(): number {
    return this.usuarios.filter(u => u.rol.toLowerCase() === 'paciente').length;
  }

  get totalJornadasDisponibles(): number {
    return this.jornadas.filter(j => j.estado === 'DISPONIBLE').length;
  }

  get totalJornadasOcupadas(): number {
    return this.jornadas.filter(j => j.estado === 'PENDIENTE' || j.estado === 'PAGADO').length;
  }

  // ==========================================
  // UTILIDADES
  // ==========================================

  formatearFechaHora(fechaStr: string): string {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleString('es-MX', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  formatearHora(fechaStr: string): string {
    if (!fechaStr) return '';
    const fecha = new Date(fechaStr);
    return fecha.toLocaleTimeString('es-MX', { hour: '2-digit', minute: '2-digit' });
  }

  limpiarMensajes() {
    this.mensajeExito = '';
    this.mensajeError = '';
  }

  cerrarSesion() {
    this.auth.cerrarSesion();
  }
}
