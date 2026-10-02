import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpParams } from '@angular/common/http';
import { ApiService } from '../../../core/services/api.service';
import { AuthService } from '../../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  loginForm: FormGroup;
  registroForm: FormGroup; // Formulario para nuevos pacientes

  vista: string = 'login'; // Controla qué pantalla se muestra
  errorMensaje: string = '';
  exitoMensaje: string = '';

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    public authService: AuthService
  ) {
    // Configuración del formulario de login
    this.loginForm = this.fb.group({
      correo: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });

    // Configuración del formulario de registro
    this.registroForm = this.fb.group({
      nombre: ['', Validators.required],
      correo: ['', [Validators.required, Validators.email]],
      password: ['', Validators.required]
    });
  }

  cambiarVista(nuevaVista: string) {
    this.vista = nuevaVista;
    this.errorMensaje = '';
    this.exitoMensaje = '';
    this.loginForm.reset();
    this.registroForm.reset();
  }

onLogin() {
    if (this.loginForm.valid) {
      // Enviamos los datos como un objeto JSON normal
      const credenciales = {
        correo: this.loginForm.value.correo,
        password: this.loginForm.value.password
      };

      /* NOTA: Si tu backend de FastAPI está configurado para pedir
         específicamente la palabra 'username' en lugar de 'correo',
         usa esta estructura en su lugar:
         const credenciales = { username: this.loginForm.value.correo, password: this.loginForm.value.password };
      */

      this.api.post('auth/login', credenciales).subscribe({
        next: (respuesta: any) => {
          this.authService.manejarLoginExitoso(respuesta);
        },
        error: (err: any) => {
          this.errorMensaje = 'Credenciales incorrectas. Intenta nuevamente.';
        }
      });
    }
  }

  onRegistro() {
    if (this.registroForm.valid) {
      this.api.post('auth/registro', this.registroForm.value).subscribe({
        next: (respuesta: any) => {
          this.exitoMensaje = 'Registro exitoso. Ahora puedes iniciar sesión.';
          this.cambiarVista('login');
        },
        error: (err: any) => {
          this.errorMensaje = err.error?.detail || 'Error al registrar el usuario.';
        }
      });
    }
  }
}
