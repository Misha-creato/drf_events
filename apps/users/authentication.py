from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomJWTAuthentication(JWTAuthentication):

    def authenticate(self, request: Request):
        view = request.resolver_match.func.cls
        permission_classes = getattr(view, 'permission_classes', [])
        if 'AllowAny' in str(permission_classes):
            return None

        return super().authenticate(request)