import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service'; // Verifica que la ruta sea correcta

@Component({
  selector: 'app-agenda',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './agenda.component.html',
  styleUrls: ['./agenda.component.scss'] // Si no tienes este archivo, créalo o quita esta línea
})
export class AgendaComponent implements OnInit {
  citas: any[] = [];
  mensaje: string = '';
  cargando: boolean = false;

  // TODO: Obtener el ID dinámicamente del usuario logueado.
  // Usamos 1 por defecto para probar la conexión.
  medicoId: number = 1;

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

  finalizarCita(citaId: number) {
    if(!confirm('¿Estás seguro de finalizar esta consulta?')) return;

    this.api.post(`doctor/appointments/${citaId}/complete`, {}).subscribe({
      next: () => {
        this.mensaje = '✅ Consulta finalizada correctamente.';
        this.cargarAgenda(); // Recargar la tabla para ver el nuevo estado
      },
      error: () => {
        this.mensaje = '❌ Error al finalizar la cita.';
        this.cdr.detectChanges();
      }
    });
  }
}
