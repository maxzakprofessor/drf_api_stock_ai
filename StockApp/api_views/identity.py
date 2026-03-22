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

class UpdatePasswordView(APIView):
    permission_classes = [IsAuthenticated] 
    def post(self, request):
        user = request.user
        new_password = request.data.get('newPassword')
        if not new_password or len(new_password) < 6:
            return Response("Пароль слишком короткий", status=400)
        user.set_password(new_password)
        # 🔥 КРИТИЧНО: Устанавливаем дату входа, чтобы убрать флаг "Mandatory Change"
        user.last_login = timezone.now() 
        user.save()
        return Response({"status": "success"})

class UserAdminView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        if not hasattr(request.user, 'profile'): return Response("No profile", status=403)
        tenant = request.user.profile.tenant
        profiles = UserProfile.objects.filter(tenant=tenant).select_related('user')
        return Response([{
            "id": p.user.id,
            "username": p.user.username,
            # ✅ Передаем флаг на фронтенд: пустой ли last_login
            "needsPasswordChange": p.user.last_login is None
        } for p in profiles])

    def post(self, request):
        if not hasattr(request.user, 'profile'): return Response("No profile", status=403)
        tenant = request.user.profile.tenant
        username = request.data.get('username')
        
        if User.objects.filter(username=username).exists():
            return Response("Логин занят", status=400)

        # 🔑 ГЕНЕРАЦИЯ ВРЕМЕННОГО ПАРОЛЯ
        temp_pass = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Создаем юзера с last_login=None (по умолчанию)
        new_user = User.objects.create_user(username=username, password=temp_pass)
        UserProfile.objects.create(user=new_user, tenant=tenant)
        
        # ✅ ОТДАЕМ ПАРОЛЬ В АНГУЛЯР, чтобы Success Modal его показала
        return Response({
            "username": username, 
            "temporaryPassword": temp_pass
        })

    def delete(self, request, pk=None):
        try:
            user_to_del = User.objects.get(pk=pk)
            if user_to_del.profile.tenant != request.user.profile.tenant:
                return Response("Access Denied", status=403)
            user_to_del.delete()
            return Response(status=204)
        except:
            return Response(status=404)
