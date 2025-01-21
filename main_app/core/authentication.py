import jwt
import uuid
import pytz
from datetime import datetime, timedelta

from rest_framework.authentication import BaseAuthentication
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        access_token = self._get_access_token_from_header(request)
        if access_token:
            return self._get_user_from_cache(access_token), None
        return None

    def get_new_access_token_and_refresh_token(self, request):
        refresh_token = request.data.get("refresh_token")
        if user_id := self._get_user_from_cache(refresh_token):
            return self._generate_access_and_refresh_tokens_and_save_to_cache(user_id)

    def _get_user_from_cache(access_token):
        try:
            user_id = cache.get(access_token)
            return User.objects.get(id=user_id)
        except Exception:
            return None

    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            if user_id := self._user_is_valid(username, password):
                return self._generate_access_and_refresh_tokens_and_save_to_cache(
                    user_id
                )

        except Exception:
            return None

    def _generate_access_and_refresh_tokens_and_save_to_cache(self, user_id):
        access_payload, refresh_payload = self._generate_payload(user_id)
        access_token = self._generate_token(access_payload)
        refresh_token = self._generate_token(refresh_payload)
        self._save_tokens_to_cache(access_token, refresh_token, user_id)
        return access_token, refresh_token

    def _user_is_valid(self, username, password):
        if user := User.objects.get(username=username).check_password(password):
            return user.id
        return None

    def _generate_payload(self, user_id):
        now = datetime.now(tz=pytz.timezone("Asia/Tehran"))
        base_payload = {
            "user_id": user_id,
            "iat": now,
            "jti": self._generate_jti(),
        }
        access_payload = base_payload.update(
            {"exp": now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_TIME)}
        )
        refresh_payload = base_payload.update(
            {"exp": now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_TIME)}
        )
        return access_payload, refresh_payload

    def _generate_jti(self):
        return uuid.uuid4().hex

    def _generate_token(self, payload):
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def _save_tokens_to_cache(self, access_token, refresh_token, user_id):
        cache.set(access_token, user_id, timeout=settings.ACCESS_TOKEN_EXPIRE_TIME)
        cache.set(refresh_token, user_id, timeout=settings.REFRESH_TOKEN_EXPIRE_TIME)

    def _get_access_token_from_header(self, request):
        return request.headers.get("Authorization")
