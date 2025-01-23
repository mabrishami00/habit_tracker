import jwt
import uuid
import pytz
import redis
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
            return self._get_user_from_access_token(access_token), None
        return None

    def get_new_access_token_and_refresh_token(self, request):
        refresh_token = request.data.get("refresh_token")
        if not self._check_if_token_is_refresh:
            return None
        user_id_and_jti = self._get_user_id_and_jti_from_token(refresh_token)
        if not user_id_and_jti:
            return None
        user_id, jti = user_id_and_jti
        self._invalidate_tokens_inside_cache(user_id, jti)
        return self._generate_access_and_refresh_tokens_and_save_to_cache(
            request, user_id
        )

    def login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        try:
            if user_id := self._user_is_valid(username, password):
                return self._generate_access_and_refresh_tokens_and_save_to_cache(
                    request, user_id
                )

        except Exception:
            return None

    def logout(self, access_token):
        user_id_and_jti = self._get_user_id_and_jti_from_token(access_token)
        if not user_id_and_jti:
            return None
        user_id, jti = user_id_and_jti
        self._invalidate_tokens_inside_cache(user_id, jti)
        return True

    def get_active_sessions_of_user(self, request):
        access_token = self._get_access_token_from_header(request)
        user_id_and_jti = self._get_user_id_and_jti_from_token(access_token)
        if not user_id_and_jti:
            return None
        user_id, _ = user_id_and_jti
        redis_client = redis.StrictRedis.from_url(
            settings.CACHES["default"]["LOCATION"]
        )
        keys = redis_client.keys(f"{user_id}*")
        sessions = []
        for key in keys:
            if session := cache.get(key):
                sessions.append(session)
        return sessions

    def _get_user_from_access_token(self, access_token):
        try:
            payload = jwt.decode(
                access_token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            if not self._check_if_token_is_access(payload):
                return None
            user_id = payload.get("user_id")
            if not cache.get(access_token):
                return None
            return User.objects.get(id=user_id)
        except Exception:
            return None

    def _get_user_id_and_jti_from_token(self, token):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if not self._check_if_token_is_refresh(payload):
                return None
            user_id = payload.get("user_id")
            jti = payload.get("jti")
            return user_id, jti

        except Exception:
            return None

    def _generate_access_and_refresh_tokens_and_save_to_cache(self, request, user_id):
        access_payload, refresh_payload, jti = self._generate_payload(user_id)
        access_token = self._generate_token(access_payload)
        refresh_token = self._generate_token(refresh_payload)
        self._save_tokens_to_cache(request, user_id, jti)
        return access_token, refresh_token

    def _user_is_valid(self, username, password):
        if user := User.objects.get(username=username).check_password(password):
            return user.id
        return None

    def _generate_payload(self, user_id):
        now = datetime.now(tz=pytz.timezone("Asia/Tehran"))
        jti = self._generate_jti()
        base_payload = {"user_id": user_id, "iat": now, "jti": jti}
        access_payload = base_payload.update(
            {
                "exp": now + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_TIME),
                "token_type": "access",
            }
        )
        refresh_payload = base_payload.update(
            {
                "exp": now + timedelta(seconds=settings.REFRESH_TOKEN_EXPIRE_TIME),
                "token_type": "refresh",
            }
        )
        return access_payload, refresh_payload, jti

    def _generate_jti(self):
        return uuid.uuid4().hex

    def _generate_token(self, payload):
        return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    def _save_tokens_to_cache(self, request, user_id, jti):
        key = self._generate_cache_key(user_id, jti)
        user_agent = self._get_user_agent_from_header(request)
        cache.set(key, user_agent, timeout=settings.ACCESS_TOKEN_EXPIRE_TIME)
        cache.set(key, user_agent, timeout=settings.REFRESH_TOKEN_EXPIRE_TIME)

    def _get_access_token_from_header(self, request):
        return request.headers.get("Authorization")

    @staticmethod
    def _get_user_agent_from_header(request):
        return request.headers.get("User-Agent")

    def _invalidate_tokens_inside_cache(self, user_id, jti):
        key = self._generate_cache_key(user_id, jti)
        keys = [key, key]
        cache.delete_many(keys)

    @staticmethod
    def _generate_cache_key(user_id, jti):
        return f"{user_id}_{jti}"

    def _check_if_token_is_access(self, payload):
        return payload.get("token_type") == "access"

    def _check_if_token_is_refresh(self, payload):
        return payload.get("token_type") == "refresh"
