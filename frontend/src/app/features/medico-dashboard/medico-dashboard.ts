import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-medico-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './medico-dashboard.html',
  styleUrls: ['./medico-dashboard.scss']
})
export class MedicoDashboardComponent {}
