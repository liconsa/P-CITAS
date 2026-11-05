import { Injectable } from '@angular/core';
import { Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  constructor(private router: Router) {}

  manejarLoginExitoso(respuestaBackend: any) {
    // Convertimos el rol a minúsculas para que coincida con nuestro switch
    const rolNormalizado = respuestaBackend.rol.toLowerCase();

    localStorage.setItem('token', respuestaBackend.access_token);
    localStorage.setItem('rol', rolNormalizado);

    // Redirigir según el rol especificado en el documento
    switch (rolNormalizado) {
      case 'admin':
      case 'administrador':
        this.router.navigate(['/admin']);
        break;
      case 'recepcionista':
        this.router.navigate(['/receptionist']);
        break;
      case 'medico':
        this.router.navigate(['/doctor']);
        break;
      case 'paciente':
        this.router.navigate(['/patient']);
        break;
      default:
        this.router.navigate(['/auth/login']);
    }
  }

  obtenerRolActual(): string | null {
    return localStorage.getItem('rol');
  }

  estaAutenticado(): boolean {
    return !!localStorage.getItem('token');
  }

  cerrarSesion() {
    // Todos los actores pueden cerrar sesión
    localStorage.removeItem('token');
    localStorage.removeItem('rol');
    this.router.navigate(['/auth/login']);
  }
}
