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

  // Conteo de citas ocupadas por día (ej. { 5: 2, 12: 6 })
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

  cargarDiasOcupadosDelMes() {
    const doctorId = this.citaForm.get('medico_id')?.value;
    if (!doctorId) return;

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
    hoy.setHours(0, 0, 0, 0);

    // Regla de negocio: mínimo 48 horas de anticipación
    const limite48h = new Date(hoy);
    limite48h.setDate(hoy.getDate() + 2);

    // Regla de negocio: máximo 3 meses (90 días) de anticipación
    const limite3Meses = new Date(hoy);
    limite3Meses.setDate(hoy.getDate() + 90);

    for (let i = 1; i <= diasEnMes; i++) {
      const fechaActual = new Date(year, month, i);
      fechaActual.setHours(0, 0, 0, 0);

      const esPasado = fechaActual < limite48h;
      const excede3Meses = fechaActual > limite3Meses;
      const esFinDeSemana = fechaActual.getDay() === 0 || fechaActual.getDay() === 6;

      const ocupadas = this.conteoDias[i] || 0;
      const estaLleno = ocupadas >= this.MAX_CITAS_DIA;

      let estadoColor = 'disponible';
      if (ocupadas > 0 && ocupadas < this.MAX_CITAS_DIA) {
        estadoColor = 'parcial';
      } else if (estaLleno) {
        estadoColor = 'lleno';
      }

      this.diasCalendario.push({
        dia: i,
        fecha: fechaActual,
        deshabilitado: esPasado || esFinDeSemana || excede3Meses,
        lleno: estaLleno,
        estado: estadoColor
      });
    }
  }

  cambiarMes(direccion: number) {
    const hoy = new Date();
    const nuevaFecha = new Date(this.mesActual.getFullYear(), this.mesActual.getMonth() + direccion, 1);

    // No permitir ir a meses pasados
    const mesMinimo = new Date(hoy.getFullYear(), hoy.getMonth(), 1);
    if (nuevaFecha < mesMinimo) {
      return;
    }

    // No permitir ir a más de 3 meses hacia adelante
    const mesMaximo = new Date(hoy.getFullYear(), hoy.getMonth() + 3, 1);
    if (nuevaFecha > mesMaximo) {
      return;
    }

    this.mesActual = nuevaFecha;
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

    const year = dia.fecha.getFullYear();
    const month = String(dia.fecha.getMonth() + 1).padStart(2, '0');
    const dayStr = String(dia.dia).padStart(2, '0');
    const fechaISO = `${year}-${month}-${dayStr}`;

    this.api.get(`patient/doctor/${doctorId}/available-hours?date=${fechaISO}`).subscribe({
      next: (data: any) => {
        this.horasDisponibles = data.horas || [];
        if (data.mensaje) {
          this.mensaje = `⚠️ ${data.mensaje}`;
        } else {
          this.mensaje = '';
        }
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.horasDisponibles = [];
        this.mensaje = err.error?.detail || 'Error al cargar horarios disponibles.';
        this.cdr.detectChanges();
      }
    });
  }

  seleccionarHora(hora: string) {
    this.horaSeleccionada = hora;

    const year = this.diaSeleccionado.fecha.getFullYear();
    const month = String(this.diaSeleccionado.fecha.getMonth() + 1).padStart(2, '0');
    const day = String(this.diaSeleccionado.dia).padStart(2, '0');

    const fechaHoraLocal = `${year}-${month}-${day}T${hora}:00`;
    this.citaForm.patchValue({ fecha_hora: fechaHoraLocal });
  }

  agendar() {
    if (this.citaForm.valid) {
      this.api.post('patient/citas', this.citaForm.value).subscribe({
        next: (res: any) => {
          this.mensaje = `✅ Cita reservada con éxito (Estado: PENDIENTE). Folio de pago generado: ${res.folio_pago || 'Generado'}. Recuerda completar el pago para confirmar tu lugar.`;
          this.cargarDiasOcupadosDelMes();
          this.diaSeleccionado = null;
          this.horaSeleccionada = '';
          this.citaForm.reset();
          this.panelDerecho = 'vacio';
          this.cdr.detectChanges();
        },
        error: (err) => {
          this.mensaje = `❌ ${err.error?.detail || 'Error al agendar la cita. El horario podría estar ocupado o pendiente de pago.'}`;
          this.cdr.detectChanges();
        }
      });
    }
  }
}
