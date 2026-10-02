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

    if (!token || !rolUsuario) {
      this.router.navigate(['/auth/login']);
      return false;
    }

    const rolesPermitidos = route.data['rolesEsperados'] as Array<string>;

    // El administrador tiene el mayor nivel de permisos dentro del sistema.[cite: 1]
    if (rolUsuario === 'administrador') {
      return true;
    }

    if (!rolesPermitidos.includes(rolUsuario)) {
      this.router.navigate(['/auth/login']); // O redirigir a una página de "Acceso Denegado"
      return false;
    }

    return true;
  }
}
