import { Component, OnInit, ChangeDetectorRef, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './admin-dashboard.html',
  styleUrl: './admin-dashboard.scss'
})
export class AdminDashboardComponent implements OnInit {
  pestanaActiva: string = 'roles'; // Mantiene la vista principal unificada

  listaUsuarios: any[] = [];
  filtroNombre: string = '';
  usuarioSeleccionado: any = null;

  // Variables de control de seguridad 2FA
  llaveEnviada: boolean = false;
  claveIngresada: string = '';

  // Áreas disponibles reducidas exclusivamente a Citas y Farmacia
  areasDisponibles: string[] = ['Citas', 'Farmacia'];

  // Variables para el control de la ventana modal de registro
  mostrarModalCrear: boolean = false;
  nuevoNombre: string = '';
  nuevoCorreo: string = '';
  nuevaContrasena: string = '';

  private apiUrl = 'http://127.0.0.1:8000/api';

  constructor(
    private router: Router,
    private http: HttpClient,
    private cdr: ChangeDetectorRef,
    private ngZone: NgZone
  ) {}

  ngOnInit() {
    this.cargarUsuariosDesdeFlask();
  }

  cargarUsuariosDesdeFlask() {
    this.http.get<any[]>(`${this.apiUrl}/usuarios`).subscribe({
      next: (data) => {
        this.ngZone.run(() => {
          this.listaUsuarios = data;
          this.cdr.detectChanges();
        });
      },
      error: (err) => {
        console.error('Error al conectar con Flask para obtener usuarios:', err);
      }
    });
  }

  // Getter exclusivo para filtrar y mostrar únicamente a las recepcionistas
  get usuariosFiltradosPorRecepcionista() {
    return this.listaUsuarios.filter(u => {
      const esRecepcionista = u.rol === 'Recepcionista';
      const coincideNombre = u.nombre.toLowerCase().includes(this.filtroNombre.toLowerCase());
      return esRecepcionista && coincideNombre;
    });
  }

  cambiarPestana(pestana: string) {
    this.pestanaActiva = pestana;
    this.usuarioSeleccionado = null;
  }

  seleccionarUsuario(usuario: any) {
    this.usuarioSeleccionado = JSON.parse(JSON.stringify(usuario));
    this.llaveEnviada = false;
    this.claveIngresada = '';
  }

  solicitarLlaveTemporal(event?: MouseEvent) {
    if (event) {
      (event.currentTarget as HTMLElement).blur();
    }

    if (!this.usuarioSeleccionado) return;

    const payload = {
      admin_email: 'admin@hospital.com',
      usuario_id: this.usuarioSeleccionado.id,
      permisos: this.usuarioSeleccionado.permisos
    };

    this.http.post(`${this.apiUrl}/seguridad/generar-token`, payload).subscribe({
      next: () => {
        this.ngZone.run(() => {
          this.llaveEnviada = true;
          this.cdr.detectChanges();
          alert('Clave temporal generada. Revisa tu consola de Python.');
        });
      },
      error: (err) => {
        this.ngZone.run(() => {
          alert('Error al generar la llave temporal.');
          console.error(err);
        });
      }
    });
  }

  // Guarda tanto los permisos como el área seleccionada de forma conjunta
  guardarPermisosConVerificacion(event?: MouseEvent) {
    if (event) {
      (event.currentTarget as HTMLElement).blur();
    }

    if (!this.claveIngresada) {
      alert('Por favor, ingresa la clave temporal.');
      return;
    }

    const payloadVerificacion = {
      admin_email: 'admin@hospital.com',
      codigo_ingresado: this.claveIngresada,
      usuario_id: this.usuarioSeleccionado.id,
      permisos: this.usuarioSeleccionado.permisos,
      area: this.usuarioSeleccionado.area // Incluimos el área en la actualización
    };

    this.http.post(`${this.apiUrl}/seguridad/verificar-y-guardar`, payloadVerificacion).subscribe({
      next: () => {
        this.ngZone.run(() => {
          alert(`¡Éxito! Cambios actualizados correctamente para ${this.usuarioSeleccionado.nombre}.`);
          this.cargarUsuariosDesdeFlask();
          this.llaveEnviada = false;
          this.claveIngresada = '';
          this.usuarioSeleccionado = null;
          this.cdr.detectChanges();
        });
      },
      error: (err: any) => {
        this.ngZone.run(() => {
          const mensajeError = err.error?.error || 'Clave temporal incorrecta o expirada.';
          alert(mensajeError);
          this.cdr.detectChanges();
        });
      }
    });
  }

  // Métodos para controlar la ventana modal flotante
  abrirModalCrear() {
    this.ngZone.run(() => {
      this.nuevoNombre = '';
      this.nuevoCorreo = '';
      this.nuevaContrasena = '';
      this.mostrarModalCrear = true;
      this.cdr.detectChanges();
    });
  }

  cerrarModalCrear() {
    this.ngZone.run(() => {
      this.mostrarModalCrear = false;
      this.cdr.detectChanges();
    });
  }

  guardarNuevaRecepcionista() {
    if (!this.nuevoNombre || !this.nuevoCorreo || !this.nuevaContrasena) {
      alert('Por favor, completa todos los campos.');
      return;
    }

    const payload = {
      nombre: this.nuevoNombre.trim(),
      correo: this.nuevoCorreo.trim(),
      contrasena: this.nuevaContrasena.trim(),
      rol: 'Recepcionista',
      area: 'Citas'
    };

    this.http.post(`${this.apiUrl}/registro`, payload).subscribe({
      next: () => {
        this.ngZone.run(() => {
          alert('¡Recepcionista registrada con éxito!');
          this.mostrarModalCrear = false;
          this.cargarUsuariosDesdeFlask();
          this.cdr.detectChanges();
        });
      },
      error: (err: any) => {
        this.ngZone.run(() => {
          alert('Error al registrar: ' + (err.error?.detail || 'Verifica los datos'));
        });
      }
    });
  }

  // Método para eliminar una recepcionista del sistema
  eliminarRecepcionista(usuario: any) {
    this.ngZone.run(() => {
      if (!confirm(`¿Estás seguro de eliminar a ${usuario.nombre}?`)) return;

      this.http.delete(`${this.apiUrl}/usuarios/${usuario.id}`).subscribe({
        next: () => {
          alert('Recepcionista eliminada correctamente.');
          this.usuarioSeleccionado = null;
          this.cargarUsuariosDesdeFlask();
          this.cdr.detectChanges();
        },
        error: (err: any) => {
          alert(err.error?.detail || 'No se pudo eliminar el registro.');
          console.error(err);
        }
      });
    });
  }

  cerrarSesion() {
    localStorage.clear();
    this.router.navigate(['/login']);
  }
}
