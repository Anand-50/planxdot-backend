import uuid
from django.db import models

class Plan(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    duration_months = models.IntegerField()

    class Meta:
        db_table = "plans"


class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    amount = models.IntegerField()
    razorpay_order_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "payments"


class Subscription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user_id = models.UUIDField()
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(max_length=20)

    class Meta:
        db_table = "subscriptions"
