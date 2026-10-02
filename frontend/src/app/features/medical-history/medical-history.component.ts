import '@angular/compiler';
import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../core/services/api.service';
import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-my-history',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './medical-history.component.html',
  styleUrl: './medical-history.component.scss'
})
export class MyHistoryComponent implements OnInit {
  historialForm: FormGroup;
  modoVista: 'formulario' | 'resumen' = 'formulario';
  esMedico: boolean = false;
  mensajeExito: string = '';
  mensajeError: string = '';
  curpVerificado: boolean = false;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private authService: AuthService,
    private cdr: ChangeDetectorRef
  ) {
    this.historialForm = this.fb.group({
      // Nombres separados
      apellido_paterno: ['', Validators.required],
      apellido_materno: ['', Validators.required],
      nombres: ['', Validators.required],

      curp: ['', [Validators.required, Validators.pattern(/^[A-Z]{4}\d{6}[HM][A-Z]{5}[0-9A-Z]{2}$/)]],
      telefono: ['', [Validators.required, Validators.minLength(10)]],

      fecha_nacimiento: [{ value: '', disabled: true }],
      edad: [{ value: '', disabled: true }],
      genero: [{ value: '', disabled: true }],
      lugar_nacimiento: [{ value: '', disabled: true }],

      // Dirección desglosada
      calle_numero: ['', Validators.required],
      colonia: ['', Validators.required],
      codigo_postal: ['', [Validators.required, Validators.pattern(/^\d{5}$/)]],
      municipio: ['', Validators.required],

      // Antecedentes tipo formato institucional
      ant_diabetes: ['NO'],
      ant_hipertension: ['NO'],
      ant_cardiacos: ['NO'],

      blood_type: ['', Validators.required],
      alergias_otro: [''],
      enfermedades_otro: [''],
      discapacidades_otro: [''],
      additional_notes: [''],
      diagnosticos_medicos: [{ value: '', disabled: true }]
    });
  }

  ngOnInit() {
    const rol = this.authService.obtenerRolActual();
    this.esMedico = (rol === 'medico' || rol === 'admin');

    if (this.esMedico) {
      this.historialForm.get('diagnosticos_medicos')?.enable();
    }

    this.cargarExpediente();
  }

  cargarExpediente() {
    this.api.get('patient/history').subscribe({
      next: (data: any) => {
        if (data) {
          this.historialForm.patchValue(data);
          if (data.curp) {
            this.curpVerificado = true;
            // Si ya cuenta con CURP guardado previamente, lo mandamos directo al resumen
            if (data.apellido_paterno) {
              this.modoVista = 'resumen';
            }
          }
        }
        this.cdr.detectChanges();
      },
      error: () => this.cdr.detectChanges()
    });
  }

  verificarCurpYAutocompletar() {
    const curpControl = this.historialForm.get('curp');
    if (!curpControl || curpControl.invalid || !curpControl.value) {
      this.mensajeError = '❌ El formato del CURP no es válido (debe tener 18 caracteres y estructura oficial).';
      this.curpVerificado = false;
      return;
    }

    const curp = curpControl.value.toUpperCase();
    this.mensajeError = '';

    try {
      const letraGenero = curp.charAt(10);
      const generoText = letraGenero === 'H' ? 'Hombre' : letraGenero === 'M' ? 'Mujer' : 'No especificado';

      const anioStr = curp.substring(4, 6);
      const mesStr = curp.substring(6, 8);
      const diaStr = curp.substring(8, 10);
      const anioNum = parseInt(anioStr, 10);
      const anioCompleto = anioNum > 30 ? `19${anioStr}` : `20${anioStr}`;

      const fechaNacimientoStr = `${anioCompleto}-${mesStr}-${diaStr}`;
      const nacimiento = new Date(fechaNacimientoStr);
      const hoy = new Date();
      let edadCalculada = hoy.getFullYear() - nacimiento.getFullYear();
      const m = hoy.getMonth() - nacimiento.getMonth();
      if (m < 0 || (m === 0 && hoy.getDate() < nacimiento.getDate())) {
        edadCalculada--;
      }

      const entidadMap: { [key: string]: string } = {
        'AS': 'Aguascalientes', 'BC': 'Baja California', 'BS': 'Baja California Sur', 'CC': 'Campeche',
        'CL': 'Coahuila', 'CM': 'Colima', 'CS': 'Chiapas', 'CH': 'Chihuahua', 'DF': 'Ciudad de México',
        'DG': 'Durango', 'GT': 'Guanajuato', 'GR': 'Guerrero', 'HG': 'Hidalgo', 'JC': 'Jalisco',
        'MC': 'Estado de México', 'MN': 'Michoacán', 'MS': 'Morelos', 'NT': 'Nayarit', 'NL': 'Nuevo León',
        'OC': 'Oaxaca', 'PL': 'Puebla', 'QO': 'Querétaro', 'QR': 'Quintana Roo', 'SP': 'San Luis Potosí',
        'SL': 'Sinaloa', 'SR': 'Sonora', 'TC': 'Tabasco', 'TS': 'Tamaulipas', 'TL': 'Tlaxcala',
        'VZ': 'Veracruz', 'YN': 'Yucatán', 'ZS': 'Zacatecas', 'NE': 'Nacido en el Extranjero'
      };
      const claveEntidad = curp.substring(11, 13);
      const lugarNacimientoText = entidadMap[claveEntidad] || 'México (Nacional)';

      this.historialForm.patchValue({
        fecha_nacimiento: fechaNacimientoStr,
        edad: edadCalculada >= 0 ? `${edadCalculada} años` : 'No calculable',
        genero: generoText,
        lugar_nacimiento: lugarNacimientoText
      });

      this.curpVerificado = true;
      this.mensajeExito = '✅ Identidad verificada y datos sociodemográficos autocompletados con éxito.';
      this.cdr.detectChanges();

    } catch (e) {
      this.mensajeError = '❌ Error al procesar el CURP. Verifica que esté bien escrito.';
      this.curpVerificado = false;
      this.cdr.detectChanges();
    }
  }

  editarDatos() {
    this.modoVista = 'formulario';
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  guardarHistorial() {
    if (this.historialForm.invalid) {
      this.mensajeError = 'Por favor completa todos los campos obligatorios.';
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    // 1. Habilitar temporalmente los campos bloqueados por el CURP para serializarlos
    this.historialForm.get('fecha_nacimiento')?.enable();
    this.historialForm.get('edad')?.enable();
    this.historialForm.get('genero')?.enable();
    this.historialForm.get('lugar_nacimiento')?.enable();

    // 2. Extraer todos los datos del formulario con getRawValue()
    const formData = this.historialForm.getRawValue();

    // 3. Volver a bloquearlos para la interfaz visual
    this.historialForm.get('fecha_nacimiento')?.disable();
    this.historialForm.get('edad')?.disable();
    this.historialForm.get('genero')?.disable();
    this.historialForm.get('lugar_nacimiento')?.disable();

    this.api.post('patient/history', formData).subscribe({
      next: () => {
        this.mensajeExito = '✅ Expediente clínico guardado y validado con éxito.';
        this.mensajeError = '';
        this.modoVista = 'resumen';
        window.scrollTo({ top: 0, behavior: 'smooth' }); // Manda la pantalla arriba en modo resumen
        this.cdr.detectChanges();
      },
      error: () => {
        this.mensajeError = '❌ Error al guardar el expediente.';
        this.mensajeExito = '';
        window.scrollTo({ top: 0, behavior: 'smooth' });
        this.cdr.detectChanges();
      }
    });
  }
}
