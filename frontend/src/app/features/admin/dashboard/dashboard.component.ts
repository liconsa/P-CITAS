import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../../core/services/api.service';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './dashboard.component.html'
})
export class DashboardComponent implements OnInit {
  usuarios: any[] = [];
  usuarioForm: FormGroup;
  mensaje: string = '';

  constructor(private api: ApiService, private fb: FormBuilder) {
    this.usuarioForm = this.fb.group({
      nombre: ['', Validators.required],
      correo: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required],
      rol: ['medico', Validators.required]
    });
  }

  ngOnInit() {
    this.cargarUsuarios();
  }

  cargarUsuarios() {
    this.api.get<any[]>('admin/usuarios').subscribe(
      res => this.usuarios = res
    );
  }

  crearUsuario() {
    if (this.usuarioForm.valid) {
      const formValue = this.usuarioForm.value;
      // El administrador podrá registrar, modificar, consultar o administrar los diferentes usuarios del sistema.[cite: 1]
      this.api.post(`admin/usuarios?rol=${formValue.rol}`, formValue).subscribe({
        next: () => {
          this.mensaje = 'Usuario creado exitosamente.';
          this.usuarioForm.reset({ rol: 'medico' });
          this.cargarUsuarios();
        },
        error: () => this.mensaje = 'Error al crear el usuario.'
      });
    }
  }
}
