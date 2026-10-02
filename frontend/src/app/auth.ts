import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  // Definimos la base de la API (ajusta el puerto si usas 5000 u 8000 según tu Flask)
  private apiUrl = 'http://127.0.0.1:8000/api'; // Nota: asegúrate de que coincida con el puerto de tu app.py (ej. 5000)

  constructor(private http: HttpClient) {}

  login(correo: string, contrasena: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login`, { correo, contrasena });
  }

  registrar(nombre: string, correo: string, contrasena: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/registro`, { nombre, correo, contrasena });
  }

  // --- NUEVOS MÉTODOS AÑADIDOS PARA LA RECUPERACIÓN ---

  solicitarRecuperacion(correo: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/solicitar-recuperacion`, { correo });
  }

  verificarCodigo(correo: string, codigo: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/verificar-codigo`, { correo, codigo });
  }

  actualizarContrasena(correo: string, nueva_contrasena: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/actualizar-contrasena`, { correo, nueva_contrasena });
  }
}
