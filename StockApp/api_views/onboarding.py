from django.contrib.auth.models import User
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
import os

from ..models import RegistrationRequest, Tenant, UserProfile

class RegisterRequestView(APIView):
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
        
        subject = f'Код активации {company}'
        message = f'Ваш код: {reg.token}'
        from_email = os.getenv('EMAIL_HOST_USER')
        
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            return Response({"message": "Код отправлен на почту"})
        except Exception as e:
            # Для тестов возвращаем токен, если почта не настроена
            return Response({
                "message": "Ошибка почты, возьмите код здесь", 
                "token": reg.token
            }, status=200)

class RegisterConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        password = request.data.get('password')
        
        if not token or not password:
            return Response("Токен и пароль обязательны", status=400)
            
        try:
            reg = RegistrationRequest.objects.get(token=token, is_confirmed=False)
            
            # 🔥 ИСПРАВЛЕНИЕ: Берем первый элемент списка (строку)
            username = reg.email.split('@')[0]
            
            # Проверка на дубликат
            if User.objects.filter(username=username).exists():
                username = f"{username}_{timezone.now().strftime('%M%S')}"

            # 1. Создаем Компанию
            new_tenant = Tenant.objects.create(name=reg.company_name)
            
            # 2. Создаем Юзера
            new_user = User.objects.create_user(username=username, email=reg.email, password=password)
            new_user.last_login = timezone.now()
            new_user.save()
            
            # 3. Связываем
            UserProfile.objects.create(user=new_user, tenant=new_tenant)
            
            reg.is_confirmed = True
            reg.save()
            
            return Response({"status": "success", "username": username})
        except RegistrationRequest.DoesNotExist:
            return Response("Неверный или уже использованный токен", status=400)
        except Exception as e:
            return Response(f"Ошибка сервера: {str(e)}", status=500)
