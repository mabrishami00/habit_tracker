from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import CreateAPIView

from main_app.seriailzers.user import UserSerializer
from main_app.core.authentication import JWTAuthentication


class UserRegisterView(CreateAPIView):
    serializer_class = UserSerializer


class UserLoginView(APIView):
    def post(self, request):
        if access_and_refresh_token := JWTAuthentication().login(request):
            access_token, refresh_token = access_and_refresh_token
            return Response(
                {
                    "result": True,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK,
            )
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


class UserLogoutView(APIView):
    def post(self, request):
        logout_response = JWTAuthentication().logout(request)
        if logout_response:
            return Response({"result": True}, status=status.HTTP_200_OK)
        return Response({"result": False}, status=status.HTTP_401_UNAUTHORIZED)


class UserActiveSessionsView(APIView):
    def post(self, request):
        user_active_sessions = JWTAuthentication().get_active_sessions_of_user(request)
        return Response({"result": user_active_sessions}, status=status.HTTP_200_OK)
