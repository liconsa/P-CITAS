import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
// Rutas relativas ajustadas a tu estructura (solo suben 2 niveles con ../../)
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './login.html'
})
export class LoginComponent {
  // Variables de control de vista y formularios
  vista: string = 'login';
  nombre: string = '';
  correo: string = '';
  contrasena: string = '';
  codigoIngresado: string = '';
  nuevaContrasena: string = '';

  // Mensajes de retroalimentación
  mensajeError: string = '';
  mensajeExito: string = '';

  constructor(private api: ApiService, public authService: AuthService) {}

  // Navegación entre las vistas de tu HTML
  cambiarVista(nuevaVista: string) {
    this.vista = nuevaVista;
    this.mensajeError = '';
    this.mensajeExito = '';
    this.correo = '';
    this.contrasena = '';
  }

  // Lógica para Iniciar Sesión[cite: 1]
  entrar(event?: Event) {
    if (event) event.preventDefault();

    const credenciales = { correo: this.correo, password: this.contrasena };

    this.api.post('auth/login', credenciales).subscribe({
      next: (respuesta: any) => {
        this.authService.manejarLoginExitoso(respuesta);
      },
      error: (err: any) => {
        this.mensajeError = 'Credenciales incorrectas. Verifica tu correo o contraseña.';
      }
    });
  }

  // Lógica para el Registro del Paciente[cite: 1]
  registrarUsuario(event?: Event) {
    if (event) event.preventDefault();

    const nuevoUsuario = {
      nombre: this.nombre,
      correo: this.correo,
      password: this.contrasena
    };

    this.api.post('auth/registro', nuevoUsuario).subscribe({
      next: () => {
        this.mensajeExito = 'Registro exitoso. Ahora puedes iniciar sesión.';
        this.cambiarVista('login');
      },
      error: (err: any) => {
        this.mensajeError = err.error?.detail || 'Ocurrió un error al intentar registrarte.';
      }
    });
  }

  // Flujo de Recuperación de Contraseña (Simulado)
  solicitarRecuperacion(event?: Event) {
    if (event) event.preventDefault();
    this.mensajeExito = 'Se ha enviado un código de recuperación a tu correo.';
    this.cambiarVista('codigo');
  }

  verificarCodigo(event?: Event) {
    if (event) event.preventDefault();
    // Simulación: el código correcto es 1234
    if (this.codigoIngresado === '1234') {
      this.cambiarVista('nueva-pass');
    } else {
      this.mensajeError = 'El código ingresado es incorrecto.';
    }
  }

  guardarNuevaContrasena(event?: Event) {
    if (event) event.preventDefault();
    this.mensajeExito = 'Tu contraseña ha sido actualizada correctamente.';
    this.cambiarVista('login');
  }
}
