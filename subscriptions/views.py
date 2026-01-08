import razorpay
import json
from datetime import timedelta
from django.http import JsonResponse
from django.conf import settings
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt

from analytics.models import AnalyticsPayment
from analytics.services import log_funnel

from .models import Plan, Payment, Subscription
from accounts.models import User


client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)




@csrf_exempt
def create_order(request):
    data = json.loads(request.body)

    plan = Plan.objects.get(id=data['plan_id'])
    user_id = data['user_id']

    order = client.order.create({
        "amount": plan.price * 100,  # Razorpay uses paise
        "currency": "INR",
        "payment_capture": 1
    })

    Payment.objects.create(
        user_id=user_id,
        plan=plan,
        amount=plan.price,
        razorpay_order_id=order['id'],
        status="created"
    )

    return JsonResponse({
        "order_id": order['id'],
        "amount": plan.price,
        "currency": "INR",
        "key": settings.RAZORPAY_KEY_ID
    })


@csrf_exempt
def verify_payment(request):
    data = json.loads(request.body)

    razorpay_order_id = data['order_id']
    user_id = data['user_id']

    # 1️⃣ Mark payment success
    payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
    payment.status = "success"
    payment.save()

    plan = payment.plan
    user = User.objects.get(id=user_id)

    # 2️⃣ Create subscription
    Subscription.objects.create(
        user_id=user_id,
        plan=plan,
        start_date=now().date(),
        end_date=now().date() + timedelta(days=plan.duration_months * 30),
        status="active"
    )

    # 3️⃣ Activate user
    User.objects.filter(id=user_id).update(subscription_status="active")

  
    # 4️⃣ Revenue analytics
    AnalyticsPayment.objects.create(
        user_id=user.id,
        plan_name=plan.name,
        amount=payment.amount,
        status="success"
    )

    # 5️⃣ Funnel analytics
    log_funnel(
        user.id,
        user.role,
        "payment_success"
    )

    return JsonResponse({"message": "Subscription activated"})
