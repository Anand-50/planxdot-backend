import json
import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import User, UserOTP

from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken

from django.core.mail import send_mail
from django.utils.timezone import now
from .models import User
from django.conf import settings



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    refresh['role'] = user.role
    refresh['email'] = user.email

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@csrf_exempt
def register(request):
    data = json.loads(request.body)

    if not data.get("legal_consent"):
        return JsonResponse(
            {"error": "Legal consent required"},
            status=400
        )

    # 🔹 Pre-check email
    if User.objects.filter(email=data["email"]).exists():
        return JsonResponse(
            {"error": "Email already registered"},
            status=409
        )

    # 🔹 Pre-check phone
    if User.objects.filter(phone=data["phone"]).exists():
        return JsonResponse(
            {"error": "Phone number already registered"},
            status=409
        )

    hashed_password = make_password(data["password"])

    try:
        user = User.objects.create(
            name=data["name"],
            email=data["email"],
            phone=data["phone"],
            password_hash=hashed_password,
            role=data["role"],

            native_country=data["native_country"],
            native_state=data["native_state"],
            native_city=data["native_city"],

            legal_consent=True,
            legal_consent_at=timezone.now()
        )
    except IntegrityError:
        # Safety net (DB-level)
        return JsonResponse(
            {"error": "User already exists"},
            status=409
        )

    email_otp = str(random.randint(100000, 999999))
    phone_otp = str(random.randint(100000, 999999))

    UserOTP.objects.bulk_create([
        UserOTP(
            target=data["email"],
            otp=email_otp,
            purpose="verify_email",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        ),
        UserOTP(
            target=data["phone"],
            otp=phone_otp,
            purpose="verify_phone",
            expires_at=timezone.now() + timezone.timedelta(minutes=5)
        )
    ])

    return JsonResponse({
        "message": "OTP sent to email & mobile"
    })


@csrf_exempt
def verify_email(request):
    data = json.loads(request.body)

    otp_obj = UserOTP.objects.filter(
        target=data["email"],
        otp=data["otp"],
        purpose="verify_email",
        used=False,
        expires_at__gt=timezone.now()
    ).first()

    if not otp_obj:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    otp_obj.used = True
    otp_obj.save()

    User.objects.filter(email=data["email"]).update(email_verified=True)

    return JsonResponse({"message": "Email verified"})


@csrf_exempt
def verify_phone(request):
    data = json.loads(request.body)

    otp_obj = UserOTP.objects.filter(
        target=data["phone"],
        otp=data["otp"],
        purpose="verify_phone",
        used=False,
        expires_at__gt=timezone.now()
    ).first()

    if not otp_obj:
        return JsonResponse({"error": "Invalid OTP"}, status=400)

    otp_obj.used = True
    otp_obj.save()

    User.objects.filter(phone=data["phone"]).update(phone_verified=True)

    return JsonResponse({"message": "Phone verified"})



@csrf_exempt
def login(request):
    data = json.loads(request.body)

    user = User.objects.filter(
        email=data['email'],
        email_verified=True,
        subscription_status='active'
    ).first()

    if not user:
        return JsonResponse({"error": "Access denied"}, status=403)

    if not check_password(data['password'], user.password_hash):
        return JsonResponse({"error": "Invalid credentials"}, status=403)

    tokens = get_tokens_for_user(user)

    return JsonResponse({
        "message": "Login success",
        "access_token": tokens['access'],
        "refresh_token": tokens['refresh']
    })


from accounts.utils import get_user_from_token
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def dashboard(request):
    try:
        user = get_user_from_token(request)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=401)

    if user.role == "entrepreneur":
        profiles = User.objects.filter(
            role="investor",
            email_verified=True,
            subscription_status="active"
        )
    else:
        profiles = User.objects.filter(
            role="entrepreneur",
            email_verified=True,
            subscription_status="active"
        )

    return JsonResponse(
        list(profiles.values("id", "name", "email")),
        safe=False
    )



def my_profile(request):
    user = get_user_from_token(request)

    settings = UserSettings.objects.filter(user_id=user.id).first()
    status = UserAccountStatus.objects.filter(user_id=user.id).first()

    return JsonResponse({
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,

        "location": {
            "country": user.native_country,
            "state": user.native_state,
            "city": user.native_city
        },

        "email_verified": user.email_verified,
        "phone_verified": user.phone_verified,

        "subscription_status": user.subscription_status,

        "settings": {
            "auto_accept_nda": settings.auto_accept_nda if settings else False,
            "require_nda_default": settings.require_nda_default if settings else True,
            "mute_notifications": settings.mute_notifications if settings else False
        },

        "account_status": {
            "is_deactivated": status.is_deactivated if status else False,
            "deletion_requested": status.deletion_requested if status else False
        }
    })


@csrf_exempt
def update_profile(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    allowed_fields = ["name", "native_country", "native_state", "native_city"]

    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])

    user.save()

    return JsonResponse({"message": "Profile updated"})


@csrf_exempt
def update_settings(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    settings, _ = UserSettings.objects.get_or_create(user_id=user.id)

    if "auto_accept_nda" in data:
        settings.auto_accept_nda = data["auto_accept_nda"]

    if "require_nda_default" in data:
        settings.require_nda_default = data["require_nda_default"]

    if "mute_notifications" in data:
        settings.mute_notifications = data["mute_notifications"]

    settings.save()

    return JsonResponse({"message": "Settings updated"})


def my_posts(request):
    user = get_user_from_token(request)

    posts = Post.objects.filter(user=user).order_by("-created_at")

    data = [{
        "post_id": str(p.id),
        "title": p.title,
        "status": p.status,
        "created_at": p.created_at
    } for p in posts]

    return JsonResponse(data, safe=False)


def my_nda_acceptances(request):
    user = get_user_from_token(request)

    records = NDAAcceptance.objects.filter(viewer=user)

    data = [{
        "post_id": str(r.post_id),
        "accepted_at": r.accepted_at
    } for r in records]

    return JsonResponse(data, safe=False)

def my_connections(request):
    user = get_user_from_token(request)

    connections = Connection.objects.filter(
        status="accepted"
    ).filter(
        requester_id=user.id
    ) | Connection.objects.filter(
        status="accepted",
        receiver_id=user.id
    )

    data = [{
        "connection_id": str(c.id),
        "user_id": str(
            c.receiver_id if c.requester_id == user.id else c.requester_id
        )
    } for c in connections]

    return JsonResponse(data, safe=False)


@csrf_exempt
def deactivate_account(request):
    user = get_user_from_token(request)

    UserAccountStatus.objects.update_or_create(
        user_id=user.id,
        defaults={
            "is_deactivated": True,
            "deactivated_at": now()
        }
    )

    return JsonResponse({"message": "Account deactivated"})


@csrf_exempt
def request_deletion(request):
    user = get_user_from_token(request)

    UserAccountStatus.objects.update_or_create(
        user_id=user.id,
        defaults={
            "deletion_requested": True,
            "deletion_requested_at": now()
        }
    )

    return JsonResponse({"message": "Deletion request submitted"})
