import { ComponentFixture, TestBed } from '@angular/core/testing';
import { StocksComponent } from './stocks.component';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { environment } from '../../../../environments/environment';
import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import * as bootstrap from 'bootstrap';

// Мокаем Bootstrap, чтобы тесты не падали в консоли
vi.mock('bootstrap', () => ({
  Modal: vi.fn().mockImplementation(() => ({
    show: vi.fn(),
    hide: vi.fn()
  }))
}));

describe('StocksComponent (Vitest)', () => {
  let component: StocksComponent;
  let fixture: ComponentFixture<StocksComponent>;
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [StocksComponent],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting()
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(StocksComponent);
    component = fixture.componentInstance;
    httpMock = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('должен загружать список складов при инициализации', () => {
    const req = httpMock.expectOne(`${environment.apiUrl}/stocks/`);
    req.flush([{ id: 1, nameStock: 'Центральный Склад' }]);

    // Проверяем работу Signal
    expect(component.stocks().length).toBe(1);
    expect(component.stocks()[0].nameStock).toBe('Центральный Склад');
  });

  it('должен отправлять POST запрос при создании нового склада', () => {
    component.nameStock = 'Тестовый Склад';
    component.createClick();

    const req = httpMock.expectOne(`${environment.apiUrl}/stocks/`);
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ nameStock: 'Тестовый Склад' });
    
    req.flush({}); // Имитируем успех
    // После успеха должен быть перезапрос GET
    httpMock.expectOne(`${environment.apiUrl}/stocks/`);
  });
});
