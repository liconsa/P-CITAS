import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-farmacia-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './farmacia-dashboard.html',
  styleUrls: ['./farmacia-dashboard.scss']
})
export class FarmaciaDashboardComponent {}
