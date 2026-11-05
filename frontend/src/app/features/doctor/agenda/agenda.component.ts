import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-agenda',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './agenda.component.html',
  styleUrls: ['./agenda.component.scss']
})
export class AgendaComponent implements OnInit {
  citas: any[] = [];
  mensaje: string = '';
  cargando: boolean = false;
  medicoId: number = 6; // Ajusta según tu ID de prueba

  // Control para mostrar el input en la fila específica
  citaActivaId: number | null = null;
  codigoIngresado: string = '';

  constructor(
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    this.cargarAgenda();
  }

  cargarAgenda() {
    this.cargando = true;
    this.api.get(`doctor/${this.medicoId}/appointments`).subscribe({
      next: (data: any) => {
        this.citas = data || [];
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar la agenda:', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  // Valida si la hora actual está dentro del horario de la cita
  // (Mismo día, desde 15 minutos antes hasta 60 minutos después de la hora programada)
  esHoraDeConsulta(fechaHoraStr: string): boolean {
    const citaDate = new Date(fechaHoraStr);
    const ahora = new Date();

    const mismoDia = citaDate.toDateString() === ahora.toDateString();
    const diffMinutos = (ahora.getTime() - citaDate.getTime()) / (1000 * 60);

    // 💡 NOTA PARA TU DEMO: Asegúrate de agendar una cita para la hora actual
    // para que el botón se active inmediatamente durante tu presentación.
    return mismoDia && diffMinutos >= -15 && diffMinutos <= 60;
  }

  iniciarFinalizacion(citaId: number) {
    this.api.post(`doctor/appointments/${citaId}/send-code`, {}).subscribe({
      next: (res: any) => {
        this.mensaje = `📲 ${res.mensaje}`;
        this.citaActivaId = citaId;
        this.codigoIngresado = '';
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.mensaje = '❌ Error al generar el código para el paciente.';
        this.cdr.detectChanges();
      }
    });
  }

  verificarYCompletar(citaId: number) {
    if (!this.codigoIngresado || this.codigoIngresado.trim() === '') {
      alert('Por favor ingresa el código de verificación.');
      return;
    }

    this.api.post(`doctor/appointments/${citaId}/verify-and-complete`, { codigo: this.codigoIngresado.trim() }).subscribe({
      next: () => {
        this.mensaje = '✅ ¡Cita finalizada exitosamente con el código del paciente!';
        this.citaActivaId = null;
        this.codigoIngresado = '';
        this.cargarAgenda();
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.mensaje = `❌ ${err.error?.detail || 'Código incorrecto.'}`;
        this.cdr.detectChanges();
      }
    });
  }

  cancelarIngreso() {
    this.citaActivaId = null;
    this.codigoIngresado = '';
    this.cdr.detectChanges();
  }
}
