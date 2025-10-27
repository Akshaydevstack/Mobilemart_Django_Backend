# notifications/middleware.py
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

@database_sync_to_async
def get_user_from_token(token_key):
    if not token_key:
        return AnonymousUser()
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        User = get_user_model()
        token = AccessToken(token_key)
        user = User.objects.get(id=token["user_id"])
        return user
    except Exception:
        return AnonymousUser()


class JWTAuthMiddleware:
    """
    Channels middleware to attach user to scope using JWT token.
    Pass token as query param: ?token=<access_token>
    """
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        query_params = parse_qs(query_string)
        token = query_params.get("token", [None])[0]
        scope["user"] = await get_user_from_token(token)
        return await self.inner(scope, receive, send)