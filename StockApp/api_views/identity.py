import random
import string
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from ..models import UserProfile
from ..serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user_name = response.data.get('username')
            user = User.objects.get(username=user_name)
            tenant_name = user.profile.tenant.name if hasattr(user, 'profile') else "No Tenant"
            # Локальный импорт для избежания циклов
            try:
                from ..session_context import identity
                identity.set_user(f"{user_name} | {tenant_name}")
            except ImportError:
                pass
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

class UserAdminView(APIView):
    # 🔥 ИСПРАВЛЕНИЕ: Меняем IsAdminUser на IsAuthenticated
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        # Проверяем, есть ли профиль и является ли он сотрудником этой компании
        if not hasattr(request.user, 'profile'): 
            return Response("No profile", status=403)
        
        tenant = request.user.profile.tenant
        profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
        return Response([{
            "id": p.user.id,
            "username": p.user.username,
            "needsPasswordChange": not p.user.last_login
        } for p in profiles])

    def post(self, request):
        if not hasattr(request.user, 'profile'): 
            return Response("No profile", status=403)
            
        tenant = request.user.profile.tenant
        username = request.data.get('username')
        if User.objects.filter(username=username).exists():
            return Response("Логин занят", status=400)

        temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        new_user = User.objects.create_user(username=username, password=temp_pass)
        UserProfile.objects.create(user=new_user, tenant=tenant)
        return Response({"username": username, "temporaryPassword": temp_pass})

    def delete(self, request, pk=None):
        if not hasattr(request.user, 'profile'): 
            return Response(status=403)
        try:
            user_to_del = User.objects.get(pk=pk)
            if user_to_del.profile.tenant != request.user.profile.tenant:
                return Response("Access Denied", status=403)
            user_to_del.delete()
            return Response(status=204)
        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)
