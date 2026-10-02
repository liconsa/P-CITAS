import { Component, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from './core/services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: 'app.component.html',
  styleUrl: 'app.scss'
})
export class AppComponent {
  title = 'hospital-frontend';

  // Variables para el efecto del menú
  isNavbarHidden = false;
  lastScrollTop = 0;

  constructor(public authService: AuthService) {}

  // Escucha el evento de scroll de la ventana
  @HostListener('window:scroll', [])
  onWindowScroll() {
    const currentScroll = window.pageYOffset || document.documentElement.scrollTop;

    // Si bajamos el scroll y pasamos de los 60px (altura aprox del header), lo ocultamos
    if (currentScroll > this.lastScrollTop && currentScroll > 60) {
      this.isNavbarHidden = true;
    } else {
      // Si subimos el scroll, lo mostramos de nuevo
      this.isNavbarHidden = false;
    }

    // Evita valores negativos en navegadores como Safari (efecto rebote)
    this.lastScrollTop = currentScroll <= 0 ? 0 : currentScroll;
  }

  logout() {
    this.authService.cerrarSesion();
  }
}
