import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

export const authGuard: CanActivateFn = (route, state) => {
  const router = inject(Router);
  const token = localStorage.getItem('token'); // Ajusta si usaste otro nombre

  if (token) {
    return true; // Si hay token, lo deja pasar
  } else {
    router.navigate(['/login']); // Si no, lo patea al login
    return false;
  }
};
