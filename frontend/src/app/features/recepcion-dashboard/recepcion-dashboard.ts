import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-recepcion-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './recepcion-dashboard.html',
  styleUrls: ['./recepcion-dashboard.scss']
})
export class RecepcionDashboardComponent {}
