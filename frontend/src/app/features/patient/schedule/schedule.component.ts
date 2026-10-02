import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-schedule',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './schedule.component.html',
  styleUrl: './schedule.component.scss'
})
export class ScheduleComponent implements OnInit {
  citaForm: FormGroup;
  mensaje: string = '';

  // Control de la vista derecha
  panelDerecho: 'vacio' | 'calendario' = 'vacio';

  // Datos Reales de la Base de Datos
  doctores: any[] = [];
  horasDisponibles: string[] = [];

  // 👈 Modificado: Ahora guardamos un diccionario con el conteo de citas por día (Ej: { 5: 2, 12: 6 })
  conteoDias: { [key: number]: number } = {};
  MAX_CITAS_DIA: number = 6;
  cargandoDoctores: boolean = false;

  // Variables del Calendario
  mesActual: Date = new Date();
  diasCalendario: any[] = [];
  nombresMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  diaSeleccionado: any = null;
  horaSeleccionada: string = '';

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {
    this.citaForm = this.fb.group({
      medico_id: ['', Validators.required],
      fecha_hora: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.cargarDoctoresReales();
    this.generarCalendario();
  }

  cargarDoctoresReales() {
    this.cargandoDoctores = true;
    this.api.get('patient/doctors').subscribe({
      next: (data: any) => {
        this.doctores = data;
        this.cargandoDoctores = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error cargando doctores:', err);
        this.cargandoDoctores = false;
        this.cdr.detectChanges();
      }
    });
  }

  onDoctorSeleccionado() {
    this.panelDerecho = 'calendario';
    this.diaSeleccionado = null;
    this.horaSeleccionada = '';
    this.citaForm.patchValue({ fecha_hora: '' });
    this.cargarDiasOcupadosDelMes();
  }

  // 👈 Modificado: Recibe el conteo de citas del backend
  cargarDiasOcupadosDelMes() {
    const doctorId = this.citaForm.get('medico_id')?.value;
    const year = this.mesActual.getFullYear();
    const month = this.mesActual.getMonth() + 1;

    this.api.get(`patient/doctor/${doctorId}/occupied-days?year=${year}&month=${month}`).subscribe({
      next: (data: any) => {
        this.conteoDias = data.conteo_por_dia || {};
        this.generarCalendario();
        this.cdr.detectChanges();
      },
      error: () => {
        this.conteoDias = {};
        this.generarCalendario();
        this.cdr.detectChanges();
      }
    });
  }

  generarCalendario() {
    const year = this.mesActual.getFullYear();
    const month = this.mesActual.getMonth();
    const primerDia = new Date(year, month, 1).getDay();
    const diasEnMes = new Date(year, month + 1, 0).getDate();

    this.diasCalendario = [];
    for (let i = 0; i < primerDia; i++) { this.diasCalendario.push(null); }

    const hoy = new Date();
    const limite48h = new Date();
    limite48h.setDate(hoy.getDate() + 2);
    limite48h.setHours(0, 0, 0, 0);

    for (let i = 1; i <= diasEnMes; i++) {
      const fechaActual = new Date(year, month, i);
      const esPasado = fechaActual < limite48h;
      const esFinDeSemana = fechaActual.getDay() === 0 || fechaActual.getDay() === 6;

      const ocupadas = this.conteoDias[i] || 0;
      const estaLleno = ocupadas >= this.MAX_CITAS_DIA;

      // Determinamos el estado visual para el HTML (disponible, parcial, lleno)
      let estadoColor = 'disponible';
      if (ocupadas > 0 && ocupadas < this.MAX_CITAS_DIA) {
        estadoColor = 'parcial'; // Amarillo
      } else if (estaLleno) {
        estadoColor = 'lleno'; // Rojo
      }

      this.diasCalendario.push({
        dia: i,
        fecha: fechaActual,
        deshabilitado: esPasado || esFinDeSemana,
        lleno: estaLleno,
        estado: estadoColor
      });
    }
  }

  cambiarMes(direccion: number) {
    this.mesActual = new Date(this.mesActual.getFullYear(), this.mesActual.getMonth() + direccion, 1);
    this.diaSeleccionado = null;
    this.horaSeleccionada = '';

    if (this.citaForm.get('medico_id')?.value) {
      this.cargarDiasOcupadosDelMes();
    } else {
      this.generarCalendario();
    }
  }

  seleccionarDia(dia: any) {
    if (!dia || dia.deshabilitado || dia.lleno) return;

    this.diaSeleccionado = dia;
    this.horaSeleccionada = '';
    this.citaForm.patchValue({ fecha_hora: '' });

    const doctorId = this.citaForm.get('medico_id')?.value;

    // Armado seguro de la fecha ISO local sin alteraciones de zona horaria
    const year = dia.fecha.getFullYear();
    const month = String(dia.fecha.getMonth() + 1).padStart(2, '0');
    const dayStr = String(dia.dia).padStart(2, '0');
    const fechaISO = `${year}-${month}-${dayStr}`;

    this.api.get(`patient/doctor/${doctorId}/available-hours?date=${fechaISO}`).subscribe({
      next: (data: any) => {
        this.horasDisponibles = data.horas || [];
        this.cdr.detectChanges();
      },
      error: () => {
        this.horasDisponibles = [];
        this.mensaje = 'Error al cargar horarios disponibles.';
        this.cdr.detectChanges();
      }
    });
  }

  // 👈 Modificado: Evita el desfase de hora asegurando el formato local exacto
  seleccionarHora(hora: string) {
    this.horaSeleccionada = hora;

    const year = this.diaSeleccionado.fecha.getFullYear();
    const month = String(this.diaSeleccionado.fecha.getMonth() + 1).padStart(2, '0');
    const day = String(this.diaSeleccionado.dia).padStart(2, '0');

    // Construimos el string exacto en formato local (Ej: "2026-10-05T09:00:00")
    const fechaHoraLocal = `${year}-${month}-${day}T${hora}:00`;

    this.citaForm.patchValue({ fecha_hora: fechaHoraLocal });
  }

  agendar() {
    if (this.citaForm.valid) {
      this.api.post('patient/citas', this.citaForm.value).subscribe({
        next: () => {
          this.mensaje = '✅ Cita agendada con éxito.';
          this.cargarDiasOcupadosDelMes();
          this.diaSeleccionado = null;
          this.horaSeleccionada = '';
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.mensaje = err.error?.detail || '❌ Error al agendar la cita. El horario podría estar ocupado.';
          this.cdr.detectChanges();
        }
      });
    }
  }
}
