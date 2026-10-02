import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-staff-management',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './staff-management.component.html',
  styleUrls: ['./staff-management.component.scss']
})
export class StaffManagementComponent implements OnInit {
  // Propiedad declarada para evitar el error de TypeScript
  medicoForm!: FormGroup;
  medicos: any[] = [];
  mensaje: string = '';
  cargando: boolean = false;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit() {
    // Inicialización del formulario reactivo
    this.medicoForm = this.fb.group({
      nombre: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      especialidad: ['', Validators.required]
    });

    this.cargarMedicos();
  }

  cargarMedicos() {
    this.cargando = true;
    this.api.get('receptionist/doctors-admin').subscribe({
      next: (data: any) => {
        this.medicos = data || [];
        this.cargando = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al cargar médicos:', err);
        this.cargando = false;
        this.cdr.detectChanges();
      }
    });
  }

  registrarMedico() {
    if (this.medicoForm.invalid) {
      this.mensaje = '❌ Por favor llena todos los campos obligatorios.';
      return;
    }

    const datosFormulario = this.medicoForm.value;

    this.api.post('receptionist/doctors-register', datosFormulario).subscribe({
      next: (response: any) => {
        this.mensaje = '✅ Médico registrado con éxito.';

        // Agregamos el médico recién creado directamente a la tabla al instante
        this.medicos.push({
          id: response.id || Date.now(),
          nombre: datosFormulario.nombre,
          email: datosFormulario.email,
          especialidad: datosFormulario.especialidad,
          activo: true
        });

        this.medicoForm.reset({ especialidad: '' }); // Limpia el formulario y resetea el select
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Error al registrar:', err);
        this.mensaje = '❌ Error al registrar el médico.';
        this.cdr.detectChanges();
      }
    });
  }

  cambiarEstado(medicoId: number) {
    this.api.post(`receptionist/doctors/${medicoId}/toggle-status`, {}).subscribe({
      next: () => {
        this.cargarMedicos();
        this.cdr.detectChanges();
      },
      error: () => {
        console.error('Error al cambiar estado del médico');
      }
    });
  }
}
