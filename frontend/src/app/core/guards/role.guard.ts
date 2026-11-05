import { Injectable } from '@angular/core';
import { CanActivate, ActivatedRouteSnapshot, RouterStateSnapshot, Router } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {
  constructor(private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const token = localStorage.getItem('token');
    const rolUsuario = localStorage.getItem('rol');

    // 1. Si de plano no tiene token o rol, va al login
    if (!token || !rolUsuario) {
      this.router.navigate(['/auth/login']);
      return false;
    }

    const rolesPermitidos = route.data['rolesEsperados'] as Array<string>;

    // 2. El administrador tiene el mayor nivel de permisos y se salta las validaciones
    if (rolUsuario === 'administrador' || rolUsuario === 'admin') {
      return true;
    }

    // 3. BLOQUEO INTELIGENTE: Si su rol no está permitido en esta URL
    if (rolesPermitidos && !rolesPermitidos.includes(rolUsuario)) {

      // En lugar de sacarlo de su cuenta, lo regresamos a su propio dashboard
      switch (rolUsuario) {
        case 'paciente':
          this.router.navigate(['/patient/dashboard']);
          break;
        case 'medico':
          this.router.navigate(['/doctor/agenda']);
          break;
        case 'recepcionista':
          this.router.navigate(['/receptionist/appointments']);
          break;
        default:
          this.router.navigate(['/auth/login']);
      }
      return false; // Bloquea la carga de la vista prohibida
    }

    // 4. Si el rol está en la lista de esperados, lo deja pasar normalmente
    return true;
  }
}
