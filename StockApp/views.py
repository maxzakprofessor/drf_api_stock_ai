import io, os, string, random
from django.db.models import Sum, F
from django.http import FileResponse
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

from django.utils import timezone
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from .models import Goods, Stocks, Goodincomes, Goodmoves, UserProfile, Tenant, Goodsales
from .serializers import (
    GoodSerializer, StockSerializer, GoodcomineSerializer, 
    GoodmoveSerializer, MyTokenObtainPairSerializer, GoodsaleSerializer
)

# =============================================================================
# 1. АВТОРИЗАЦИЯ И ПРОФИЛЬ (SAAS IDENTITY)
# =============================================================================

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user_name = response.data.get('username')
            user = User.objects.get(username=user_name)
            tenant_name = user.profile.tenant.name if hasattr(user, 'profile') else "No Tenant"
            from .session_context import identity
            identity.set_user(f"{user_name} | {tenant_name}")
        return response

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        user = request.user
        new_password = request.data.get('newPassword')
        if not new_password or len(new_password) < 6:
            return Response("Пароль слишком короткий", status=400)
        user.set_password(new_password)
        user.last_login = timezone.now() 
        user.save()
        return Response({"status": "success"})

# =============================================================================
# 2. УПРАВЛЕНИЕ ПЕРСОНАЛОМ (ИЗОЛЯЦИЯ АДМИНКИ)
# =============================================================================

class UserAdminView(APIView):
    permission_classes = [IsAdminUser] 

    def get(self, request):
        if not hasattr(request.user, 'profile'): return Response([])
        tenant = request.user.profile.tenant
        profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
        return Response([{
            "id": p.user.id,
            "username": p.user.username,
            "needsPasswordChange": not p.user.last_login
        } for p in profiles])

    def post(self, request):
        if not hasattr(request.user, 'profile'): return Response("No profile", status=403)
        tenant = request.user.profile.tenant
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response("Логин занят", status=400)

        temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        new_user = User.objects.create_user(username=username, password=temp_pass)
        UserProfile.objects.create(user=new_user, tenant=tenant)
        return Response({"username": username, "temporaryPassword": temp_pass})

    def delete(self, request, pk=None):
        if not hasattr(request.user, 'profile'): return Response(status=403)
        try:
            user_to_del = User.objects.get(pk=pk)
            if user_to_del.profile.tenant != request.user.profile.tenant:
                return Response("Access Denied", status=403)
            user_to_del.delete()
            return Response(status=204)
        except: return Response(status=404)

# =============================================================================
# 3. СКЛАДСКОЙ УЧЕТ (SAAS FILTERING & ISOLATION)
# =============================================================================

class MultiTenantViewSet(viewsets.ModelViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_tenant(self):
        if hasattr(self.request.user, 'profile'):
            return self.request.user.profile.tenant
        return None

class GoodViewSet(MultiTenantViewSet):
    serializer_class = GoodSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Goods.objects.filter(tenant=tenant) if tenant else Goods.objects.none()
    def perform_create(self, serializer):
        # Товары имеют поле tenant напрямую
        serializer.save(tenant=self.get_tenant())

class StockViewSet(MultiTenantViewSet):
    serializer_class = StockSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Stocks.objects.filter(tenant=tenant) if tenant else Stocks.objects.none()
    def perform_create(self, serializer):
        # Склады имеют поле tenant напрямую
        serializer.save(tenant=self.get_tenant())

class GoodIncomeViewSet(MultiTenantViewSet):
    serializer_class = GoodcomineSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Goodincomes.objects.filter(stock__tenant=tenant).select_related('stock', 'good') if tenant else Goodincomes.objects.none()
    def perform_create(self, serializer):
        # У ПРИХОДОВ НЕТ ПОЛЯ TENANT (фильтрация через stock)
        serializer.save()

class GoodMoveViewSet(MultiTenantViewSet):
    serializer_class = GoodmoveSerializer
    def get_queryset(self):
        tenant = self.get_tenant()
        return Goodmoves.objects.filter(stockFrom__tenant=tenant).select_related('stockFrom', 'stockTo', 'good') if tenant else Goodmoves.objects.none()
    def perform_create(self, serializer):
        # У ПЕРЕМЕЩЕНИЙ НЕТ ПОЛЯ TENANT (фильтрация через stockFrom)
        serializer.save()

# =============================================================================
# 4. АНАЛИТИКА (ИЗОЛИРОВАННЫЕ ОТЧЕТЫ)
# =============================================================================

class GoodRestView(APIView):
    permission_classes = [IsAuthenticated]

    def get_balances(self, request, wnameStock, wnameGood):
        if not hasattr(request.user, 'profile'): return []
        tenant = request.user.profile.tenant
        balances = {}

        # 1. ПРИХОДЫ (+)
        inc = Goodincomes.objects.filter(stock__tenant=tenant).values(
            s=F('stock__nameStock'), g=F('good__nameGood')
        ).annotate(t=Sum('qty'))
        for r in inc: 
            balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) + r['t']
        
        # 2. ПЕРЕМЕЩЕНИЯ ИЗ (-)
        m_from = Goodmoves.objects.filter(stockFrom__tenant=tenant).values(
            s=F('stockFrom__nameStock'), g=F('good__nameGood')
        ).annotate(t=Sum('qty'))
        for r in m_from: 
            balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) - r['t']
            
        # 3. ПЕРЕМЕЩЕНИЯ В (+)
        m_to = Goodmoves.objects.filter(stockTo__tenant=tenant).values(
            s=F('stockTo__nameStock'), g=F('good__nameGood')
        ).annotate(t=Sum('qty'))
        for r in m_to: 
            balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) + r['t']

        # 4. ПРОДАЖИ (-) — НОВЫЙ БЛОК
        sales = Goodsales.objects.filter(stock__tenant=tenant).values(
            s=F('stock__nameStock'), g=F('good__nameGood')
        ).annotate(t=Sum('qty'))
        for r in sales:
            balances[(r['s'], r['g'])] = balances.get((r['s'], r['g']), 0) - r['t']

        # Формируем итоговый список
        res = [{"nameStock": k[0], "nameGood": k[1], "qty": v} for k, v in balances.items()]
        
        # Фильтрация
        if wnameStock != "All": res = [r for r in res if r['nameStock'] == wnameStock]
        if wnameGood != "All": res = [r for r in res if r['nameGood'] == wnameGood]
        
        return sorted(res, key=lambda x: (x['nameStock'], x['nameGood']))

    def get(self, request, wnameStock="All", wnameGood="All"):
        return Response(self.get_balances(request, wnameStock, wnameGood))

    def post(self, request, wnameStock="All", wnameGood="All"):
        data = self.get_balances(request, wnameStock, wnameGood)
        buffer = io.BytesIO()
        
        # 1. Поиск и регистрация шрифта с поддержкой кириллицы
        f_name = "Helvetica"
        paths = [
            "C:/Windows/Fonts/arial.ttf", 
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"
        ]
        for p in paths:
            if os.path.exists(p):
                pdfmetrics.registerFont(TTFont('RusFont', p))
                f_name = 'RusFont'
                break

        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # 2. Настройка стиля заголовка (КРИТИЧНО для кириллицы)
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.fontName = f_name  # Устанавливаем шрифт, который понимает русский язык
        
        tenant_name = request.user.profile.tenant.name if hasattr(request.user, 'profile') else "Sklad PRO"
        elements.append(Paragraph(f"Отчет компании: {tenant_name}", title_style))

        # 3. Подготовка данных таблицы
        table_data = [["Склад", "Товар", "Остаток"]]
        for item in data:
            table_data.append([item['nameStock'], item['nameGood'], str(item['qty'])])

        # 4. Настройка таблицы и применение шрифта ко всем ячейкам
        t = Table(table_data, colWidths=[180, 180, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.dodgerblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, -1), f_name),  # Применяем шрифт здесь
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(t)
        doc.build(elements)
        buffer.seek(0)
        
        return FileResponse(buffer, as_attachment=True, filename='Report.pdf')


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        if not hasattr(request.user, 'profile'):
            return Response({"cards": {"goods": 0, "stocks": 0, "operations": 0}})
        
        tenant = request.user.profile.tenant
        # Считаем только то, что принадлежит этой компании
        return Response({
            "cards": {
                "goods": Goods.objects.filter(tenant=tenant).count(),
                "stocks": Stocks.objects.filter(tenant=tenant).count(),
                "operations": Goodincomes.objects.filter(stock__tenant=tenant).count()
            },
            "chart": {"labels": [], "datasets": []} 
        })


class AIAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        return Response({"report": "ИИ: Оптимизируйте закупки для вашей компании."})

# =============================================================================
# 5. СИСТЕМА РЕГИСТРАЦИИ НОВЫХ КОМПАНИЙ (SAAS ONBOARDING)
# =============================================================================
from .models import RegistrationRequest
from django.core.mail import send_mail

class RegisterRequestView(APIView):
    """Шаг 1: Клиент вводит Email и Имя компании"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        company = request.data.get('companyName')
        
        if not email or not company:
            return Response("Заполните все поля", status=400)
            
        reg, created = RegistrationRequest.objects.get_or_create(
            email=email, 
            defaults={'company_name': company}
        )
        
        # --- АКТИВАЦИЯ EMAIL ---
        subject = f'Активация вашей компании {company} в Sklad PRO'
        message = f"""
        Здравствуйте! 
        
        Спасибо за регистрацию в Sklad PRO SaaS. 
        Ваш код активации для компании "{company}":
        
        {reg.token}
        
        Введите этот код на странице подтверждения, чтобы создать аккаунт администратора.
        """
        from_email = 'noreply@skladpro.kz' # Этот email должен совпадать с EMAIL_HOST_USER в settings
        
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            print(f"✅ Письмо успешно отправлено на {email}")
        except Exception as e:
            print(f"❌ Ошибка отправки почты: {e}")
            # Для тестов все равно возвращаем токен в ответе, чтобы ты мог его скопировать без почты
            return Response({
                "message": "Ошибка отправки письма, но токен создан (см. консоль)", 
                "token": reg.token
            }, status=200)
        
        return Response({"message": "Инструкции отправлены на ваш Email"})




class RegisterConfirmView(APIView):
    """Шаг 2: Клиент вводит ТОКЕН и ПАРОЛЬ (создаем SaaS-окружение)"""
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        
        try:
            reg = RegistrationRequest.objects.get(token=token, is_confirmed=False)
            
            # 1. Создаем Компанию (Tenant)
            new_tenant = Tenant.objects.create(name=reg.company_name)
            
            # 2. Создаем Администратора (User)
            username = reg.email.split('@')[0]
            new_user = User.objects.create_user(username=username, email=reg.email, password=password)
            
            # ГЛАВНЫЙ ФИКС: Ставим дату входа ПРЯМО СЕЙЧАС
            # Это скажет системе, что директор уже сам задал пароль и менять его НЕ НУЖНО
            new_user.last_login = timezone.now()
            
            new_user.is_staff = True 
            new_user.save()
            
            # 3. Привязываем Админа к Компании
            UserProfile.objects.create(user=new_user, tenant=new_tenant)
            
            reg.is_confirmed = True
            reg.save()
            
            return Response({"status": "success", "username": username})
            
        except RegistrationRequest.DoesNotExist:
            return Response("Неверный токен", status=400)


# =============================================================================
# 6. ПРОДАЖИ (SAAS SALES MODULE)
# =============================================================================

class GoodSaleViewSet(MultiTenantViewSet):
    serializer_class = GoodsaleSerializer
    
    def get_queryset(self):
        tenant = self.get_tenant()
        # Показываем продажи только тех складов, которые принадлежат этой компании
        return Goodsales.objects.filter(stock__tenant=tenant).select_related('stock', 'good')
    
    def perform_create(self, serializer):
        # При создании продажи просто сохраняем (tenant подтянется через stock)
        serializer.save()

