from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView

from seriailzers.user import UserSerializer


class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


class UserLoginView(APIView):
    def post(self, request):
        username, password = request.data.get("username"), request.data.get("password")
        if authenticate(username=username, password=password):
            return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_401_UNAUTHORIZED)