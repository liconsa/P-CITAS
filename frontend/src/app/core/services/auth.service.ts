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
      case 'admin': // Coincide con el ENUM 'ADMIN' de la base de datos
        this.router.navigate(['/admin']);
        break;
      case 'recepcionista': // Coincide con 'RECEPCIONISTA'
        this.router.navigate(['/receptionist']);
        break;
      case 'medico': // Coincide con 'MEDICO'
        this.router.navigate(['/doctor']);
        break;
      case 'paciente': // Coincide con 'PACIENTE'
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
