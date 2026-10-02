import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-prescriptions',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './prescriptions.component.html'
})
export class PrescriptionsComponent {
  recetaForm: FormGroup;
  mensaje: string = '';

  constructor(private fb: FormBuilder, private api: ApiService) {
    this.recetaForm = this.fb.group({
      paciente_id: ['', Validators.required],
      diagnostico: ['', Validators.required],
      medicamentos: ['', Validators.required] // En una versión avanzada, esto sería un FormArray
    });
  }

  generarReceta() {
    if (this.recetaForm.valid) {
      // El médico podrá registrar recetas médicas relacionadas con un paciente.
      this.api.post('doctor/recetas', this.recetaForm.value).subscribe({
        next: () => {
          this.mensaje = 'Receta médica generada y guardada correctamente.';
          this.recetaForm.reset();
        },
        error: () => {
          this.mensaje = 'Ocurrió un error al generar la receta.';
        }
      });
    }
  }
}
