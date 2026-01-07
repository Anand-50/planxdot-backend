
import uuid
from django.db import models


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    name = models.TextField()
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True)  # 📱 mobile number

    password_hash = models.TextField()
    role = models.CharField(max_length=20)

    # ✅ Native (permanent) location
    native_country = models.CharField(max_length=100)
    native_state = models.CharField(max_length=100)
    native_city = models.CharField(max_length=100)

    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)

    subscription_status = models.CharField(max_length=20, default='pending')

    is_suspended = models.BooleanField(default=False)
    suspended_reason = models.TextField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)

    legal_consent = models.BooleanField(default=False)
    legal_consent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'users'



class UserOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    target = models.CharField(max_length=100)  
    # email OR phone

    otp = models.CharField(max_length=6)

    purpose = models.CharField(
        max_length=30,
        choices=[
            ("verify_email", "verify_email"),
            ("verify_phone", "verify_phone"),
            ("reset_password", "reset_password"),
        ]
    )

    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "user_otps"
