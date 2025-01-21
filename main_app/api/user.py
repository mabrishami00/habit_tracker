from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView

from seriailzers.user import UserSerializer
from core.authentication import JWTAuthentication


class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


class UserLoginView(APIView):
    def post(self, request):
        username, password = request.data.get("username"), request.data.get("password")
        if authenticate(username=username, password=password):
            return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_401_UNAUTHORIZED)


class UserGetNewTokens(APIView):
    def post(self, request):
        access_token, refresh_token = (
            JWTAuthentication().get_new_access_token_and_refresh_token(request)
        )
        if access_token and refresh_token:
            return Response(
                {
                    "result": True,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )
        return Response({"result": False}, status=status.HTTP_401_UNAUTHORIZED)
