from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView

from seriailzers.user import UserSerializer


class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


