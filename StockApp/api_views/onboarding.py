from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import RegistrationRequest, Tenant, UserProfile

class RegisterRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        return Response({"message": "Token sent"})

class RegisterConfirmView(APIView):
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        return Response({"status": "success"})
