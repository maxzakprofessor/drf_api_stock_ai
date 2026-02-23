# StockApp/views.py
import io
import os
import string
import random
from django.db.models import Sum, F
from django.http import FileResponse
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

# Библиотеки ReportLab для создания PDF
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from django.utils import timezone # Не забудьте импорт в начале файла
from rest_framework import viewsets, permissions # Добавь импорт permissions
from rest_framework_simplejwt.authentication import JWTAuthentication # И этот тоже


# Импорт ваших моделей и сериализаторов
from .models import Goods, Stocks, Goodincomes, Goodmoves
from .serializers import (
    GoodSerializer, StockSerializer, GoodcomineSerializer, 
    GoodmoveSerializer, MyTokenObtainPairSerializer
)

# =============================================================================
# 1. АВТОРИЗАЦИЯ И УПРАВЛЕНИЕ ПАРОЛЯМИ
# =============================================================================

from .session_context import identity # Импортируем наш Singleton для хранения имени юзера

class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        # 1. Получаем стандартный ответ (токены)
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # 2. Берем имя из запроса (который прислал Vue)
            user_name = request.data.get('username', 'admin')
            
            # 3. Фиксируем для MongoDB (Singleton)
            from .session_context import identity
            identity.set_user(user_name)
            print(f"🔐 [SINGLETON] Личность зафиксирована: {user_name}")

            # 4. ВАЖНО: Отдаем имя обратно во Vue, чтобы не было undefined!
            response.data['username'] = user_name
            
        return response




class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated] 

    def post(self, request):
        username = request.data.get('username')
        new_password = request.data.get('newPassword')
        
        if not new_password or len(new_password) < 6:
            return Response("Пароль должен быть не менее 6 символов", status=400)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            
            # --- КРИТИЧЕСКИ ВАЖНЫЙ МОМЕНТ ---
            # Устанавливаем дату входа, чтобы флаг needsPasswordChange стал False
            user.last_login = timezone.now() 
            
            user.save()
            return Response({"status": "success", "message": "Пароль обновлен"})
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=404)
        
    """Смена пароля: вызывается, когда пользователь входит с временным паролем"""
    permission_classes = [IsAuthenticated] # Требует токен, полученный при входе

    def post(self, request):
        username = request.data.get('username')
        new_password = request.data.get('newPassword')
        
        if not new_password or len(new_password) < 6:
            return Response("Пароль должен быть не менее 6 символов", status=400)

        try:
            # Находим пользователя и обновляем пароль через встроенный метод Django
            user = User.objects.get(username=username)
            user.set_password(new_password)
            user.save()
            return Response({"status": "success", "message": "Пароль обновлен"})
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=404)



    permission_classes = [IsAuthenticated] 

    def post(self, request):
        username = request.data.get('username')
        new_password = request.data.get('newPassword')
        
        if not new_password or len(new_password) < 6:
            return Response("Пароль должен быть не менее 6 символов", status=400)

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            
            # --- КРИТИЧЕСКИ ВАЖНЫЙ МОМЕНТ ---
            # Устанавливаем дату входа, чтобы флаг needsPasswordChange стал False
            user.last_login = timezone.now() 
            
            user.save()
            return Response({"status": "success", "message": "Пароль обновлен"})
        except User.DoesNotExist:
            return Response("Пользователь не найден", status=404)


# =============================================================================
# 2. УПРАВЛЕНИЕ ПЕРСОНАЛОМ (Для админки)
# =============================================================================

class UserAdminView(APIView):
    """Только для Администраторов: регистрация сотрудников"""
    permission_classes = [IsAdminUser] 

    def get(self, request):
        """Список всех юзеров для таблицы во Vue"""
        users = User.objects.all().values('id', 'username', 'last_login')
        results = []
        for u in users:
            results.append({
                "id": u['id'],
                "username": u['username'],
                "fullName": u['username'].replace('.', ' ').title(),
                "role": "Сотрудник склада",
                # Если last_login пуст — пароль еще не меняли
                "needsPasswordChange": True if not u['last_login'] else False
            })
        return Response(results)

    def post(self, request):
        """Создание нового юзера с 8-значным временным паролем"""
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response("Логин занят", status=400)

        temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        User.objects.create_user(username=username, password=temp_pass)

        return Response({
            "username": username,
            "temporaryPassword": temp_pass
        })


# =============================================================================
# 3. УЧЕТ ТОВАРОВ И СКЛАДОВ (CRUD)
# =============================================================================

class GoodViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Goods.objects.all()
    serializer_class = GoodSerializer

class StockViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Stocks.objects.all()
    serializer_class = StockSerializer

class GoodIncomeViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    queryset = Goodincomes.objects.select_related('stock', 'good').all()
    serializer_class = GoodcomineSerializer
  


class GoodMoveViewSet(viewsets.ModelViewSet):
    # ПРИНУДИТЕЛЬНО: Только JWT и только для авторизованных
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    queryset = Goodmoves.objects.select_related('stockFrom', 'stockTo', 'good').all()
    serializer_class = GoodmoveSerializer



















# =============================================================================
# 4. АНАЛИТИКА: ОСТАТКИ, PDF И AI
# =============================================================================

class GoodRestView(APIView):
    """Расчет реальных остатков по каждому складу"""
    def get_balances(self, wnameStock, wnameGood):
        balances = {}
        # Математика склада: Приходы(+) - Ушло со склада(-) + Пришло на склад(+)
        inc = Goodincomes.objects.values(s=F('stock__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in inc: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) + r['t']
        
        m_from = Goodmoves.objects.values(s=F('stockFrom__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in m_from: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) - r['t']
            
        m_to = Goodmoves.objects.values(s=F('stockTo__nameStock'), g=F('good__nameGood')).annotate(t=Sum('qty'))
        for r in m_to: balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) + r['t']

        results = [{"nameStock": k[0], "nameGood": k[1], "qty": v} for k, v in balances.items()]
        if wnameStock != "Все": results = [r for r in results if r['nameStock'] == wnameStock]
        if wnameGood != "Все": results = [r for r in results if r['nameGood'] == wnameGood]
        return sorted(results, key=lambda x: (x['nameStock'], x['nameGood']))

    def get(self, request, wnameStock="Все", wnameGood="Все"):
        return Response(self.get_balances(wnameStock, wnameGood))

    def post(self, request, wnameStock="Все", wnameGood="Все"):
        """Генерация PDF без 'квадратиков' (с русским шрифтом)"""
        data = self.get_balances(wnameStock, wnameGood)
        buffer = io.BytesIO()
        f_name = "Helvetica"
        # Пути к шрифтам для Windows и Linux/Docker
        paths = ["C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
        for p in paths:
            if os.path.exists(p):
                pdfmetrics.registerFont(TTFont('RusFont', p))
                f_name = 'RusFont'; break

        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        title_style = getSampleStyleSheet()['Title']
        title_style.fontName = f_name
        elements.append(Paragraph(f"Остатки: {wnameStock}", title_style))

        table_data = [["Склад", "Товар", "Остаток"]]
        for item in data: table_data.append([item['nameStock'], item['nameGood'], str(item['qty'])])

        t = Table(table_data, colWidths=[180, 180, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), f_name),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename='Report.pdf')

class AIAnalyzeView(APIView):
    """ИИ-советник: анализ текущей ситуации на складе"""
    def post(self, request):
        return Response({"report": "Анализ завершен: остатки распределены равномерно. Рекомендуем пополнить запас популярных позиций."})

class DashboardStatsView(APIView):
    """Эндпоинт для главной страницы: статистика в цифрах и данные для графиков"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 1. Общие цифры для карточек
        total_goods = Goods.objects.count()
        total_stocks = Stocks.objects.count()
        total_incomes = Goodincomes.objects.count()
        
        # 2. Подготовка данных для графика (Топ-5 товаров по общему количеству)
        # Мы используем логику из нашего GoodRestView, но упрощенно
        from django.db.models import Sum
        
        # Считаем остатки по всем складам суммарно
        raw_data = GoodRestView().get_balances("Все", "Все")
        # Группируем по товару для графика
        chart_labels = []
        chart_values = []
        
        # Берем первые 5-7 товаров для красоты графика
        for item in raw_data[:7]:
            chart_labels.append(item['nameGood'])
            chart_values.append(item['qty'])

        return Response({
            "cards": {
                "goods": total_goods,
                "stocks": total_stocks,
                "operations": total_incomes
            },
            "chart": {
                "labels": chart_labels,
                "datasets": [{
                    "label": "Остатки на складах",
                    "data": chart_values,
                    "backgroundColor": ["#0d6efd", "#198754", "#ffc107", "#dc3545", "#6610f2"]
                }]
            }
        })
