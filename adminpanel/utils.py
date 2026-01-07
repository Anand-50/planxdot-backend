from rest_framework_simplejwt.authentication import JWTAuthentication
from adminpanel.models import AdminUser

from adminpanel.permissions import ROLE_PERMISSIONS


def get_admin_from_token(request):
    jwt_auth = JWTAuthentication()
    validated = jwt_auth.authenticate(request)

    if not validated:
        raise Exception("Unauthorized")

    user, token = validated

    admin = AdminUser.objects.filter(
        email=user.email,
        is_active=True
    ).first()

    if not admin:
        raise Exception("Not admin")

    return admin



def require_permission(admin, permission):
    allowed = ROLE_PERMISSIONS.get(admin.role, [])

    if "*" in allowed:
        return

    if permission not in allowed:
        raise Exception("Permission denied")

