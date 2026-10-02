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
  diasOcupados: number[] = [];
  cargandoDoctores: boolean = false; // Indicador de carga para la UI

  // Variables del Calendario
  mesActual: Date = new Date();
  diasCalendario: any[] = [];
  nombresMeses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
  diaSeleccionado: any = null;
  horaSeleccionada: string = '';

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private cdr: ChangeDetectorRef // 👈 Inyección para forzar la actualización visual
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

  // 1. OBTENER DOCTORES DEL BACKEND CON ESTADO DE CARGA Y DETECCIÓN DE CAMBIOS
  cargarDoctoresReales() {
    this.cargandoDoctores = true;
    this.api.get('patient/doctors').subscribe({
      next: (data: any) => {
        this.doctores = data;
        this.cargandoDoctores = false;
        this.cdr.detectChanges(); // 👈 Fuerza al navegador a pintar los datos al instante
      },
      error: (err) => {
        console.error('Error cargando doctores:', err);
        this.cargandoDoctores = false;
        this.cdr.detectChanges();
      }
    });
  }

  // Evento al cambiar de doctor en el Select
  onDoctorSeleccionado() {
    this.panelDerecho = 'calendario';
    this.diaSeleccionado = null;
    this.horaSeleccionada = '';
    this.citaForm.patchValue({ fecha_hora: '' });
    this.cargarDiasOcupadosDelMes();
  }

  // 2. OBTENER DÍAS LLENOS DEL BACKEND
  cargarDiasOcupadosDelMes() {
    const doctorId = this.citaForm.get('medico_id')?.value;
    const year = this.mesActual.getFullYear();
    const month = this.mesActual.getMonth() + 1; // +1 porque en JS los meses empiezan en 0

    this.api.get(`patient/doctor/${doctorId}/occupied-days?year=${year}&month=${month}`).subscribe({
      next: (data: any) => {
        this.diasOcupados = data.dias_ocupados || [];
        this.generarCalendario();
        this.cdr.detectChanges();
      },
      error: () => {
        this.diasOcupados = [];
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
      const estaLleno = this.diasOcupados.includes(i);

      this.diasCalendario.push({
        dia: i,
        fecha: fechaActual,
        deshabilitado: esPasado || esFinDeSemana,
        lleno: estaLleno
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
    const fechaISO = new Date(dia.fecha.getTime() - (dia.fecha.getTimezoneOffset() * 60000)).toISOString().split('T')[0];

    // 3. OBTENER HORAS DISPONIBLES DEL BACKEND
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

  seleccionarHora(hora: string) {
    this.horaSeleccionada = hora;
    const [horas, minutos] = hora.split(':');
    const fechaFinal = new Date(this.diaSeleccionado.fecha);
    fechaFinal.setHours(Number(horas), Number(minutos));

    const fechaISO = fechaFinal.toISOString().slice(0, 16);
    this.citaForm.patchValue({ fecha_hora: fechaISO });
  }

  agendar() {
    if (this.citaForm.valid) {
      // 4. GUARDAR CITA REAL EN EL BACKEND
      this.api.post('patient/citas', this.citaForm.value).subscribe({
        next: () => {
          this.mensaje = '✅ Cita agendada con éxito.';
          this.cargarDiasOcupadosDelMes();
          this.diaSeleccionado = null;
          this.cdr.detectChanges();
        },
        error: () => {
          this.mensaje = '❌ Error al agendar la cita. El horario podría estar ocupado.';
          this.cdr.detectChanges();
        }
      });
    }
  }
}
