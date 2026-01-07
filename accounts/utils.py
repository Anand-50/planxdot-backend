from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User

def get_user_from_token(request):
    auth = JWTAuthentication()

    try:
        validated_token = auth.get_validated_token(
            auth.get_raw_token(
                auth.get_header(request)
            )
        )
    except Exception:
        raise AuthenticationFailed("Invalid or missing token")

    user_id = validated_token.get("user_id")

    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise AuthenticationFailed("User not found")
