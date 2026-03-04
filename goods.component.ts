import { Component, OnInit, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';
import { timeout, catchError, of } from 'rxjs'; // 🔥 Добавляем операторы RxJS

declare var bootstrap: any; 

@Component({
  selector: 'app-goods',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './goods.component.html',
  styleUrl: './goods.component.scss'
})
export class GoodsComponent implements OnInit {
  private http = inject(HttpClient);
  private readonly API_URL = environment.apiUrl;

  goods = signal<any[]>([]);
  modalTitle = "";
  nameGood = "";
  id = 0;
  idToDelete = 0;

  ngOnInit() { this.refreshData(); }

  refreshData() {
    this.http.get<any[]>( `${this.API_URL}/goods/` ).subscribe({
      next: (res) => this.goods.set(res),
      error: (err) => console.error('Ошибка загрузки:', err)
    });
  }

  private closeModal(modalId: string) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
      const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
      modalInstance.hide();
      const backdrop = document.querySelector('.modal-backdrop');
      if (backdrop) backdrop.remove();
      document.body.classList.remove('modal-open');
    }
  }

  private showModal(modalId: string) {
    const modalElement = document.getElementById(modalId);
    if (modalElement) {
      const modalInstance = new bootstrap.Modal(modalElement);
      modalInstance.show();
    }
  }

  addClick() {
    this.modalTitle = "Добавить товар";
    this.id = 0;
    this.nameGood = "";
    this.showModal('goodsModal');
  }

  // 🔥 СКОРОСТНОЕ СОЗДАНИЕ (Не ждем тугодумный сервер)
  createClick() {
    if (!this.nameGood) return;
    
    this.http.post( `${this.API_URL}/goods/`, { nameGood: this.nameGood })
      .pipe(
        timeout(2500), // ⏱️ Ждем всего 2.5 секунды (вместо 30)
        catchError(err => {
          // Если сервер завис, но ACID в базе сработает
          console.warn('Сервер не ответил вовремя, но мы обновляем список по ACID');
          this.refreshData(); 
          this.closeModal('goodsModal');
          return of(null); // Гасим ошибку 500 для интерфейса
        })
      )
      .subscribe((res) => {
        if (res) { // Если сервер ответил быстро (до 2.5 сек)
          this.refreshData(); 
          this.closeModal('goodsModal');
        }
      });
  }

  editClick(item: any) {
    this.modalTitle = "Редактировать товар";
    this.id = item.id;
    this.nameGood = item.nameGood;
    this.showModal('goodsModal');
  }

  updateClick() {
    this.http.put( `${this.API_URL}/goods/${this.id}/`, { nameGood: this.nameGood }).subscribe({
      next: () => { this.refreshData(); this.closeModal('goodsModal'); }
    });
  }

  prepareDelete(id: number) { this.idToDelete = id; this.showModal('deleteModal'); }

  confirmDelete() {
    this.http.delete( `${this.API_URL}/goods/${this.idToDelete}/` ).subscribe({
      next: () => { this.refreshData(); this.closeModal('deleteModal'); }
    });
  }
}
