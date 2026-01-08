from django.utils.timezone import now, timedelta
from django.db.models import Count, Sum

from accounts.models import User
from posts.models import Post
from subscriptions.models import Subscription, Payment
from chat.models import ChatThread
from reports.models import Report   # if you have it
from posts.models import NDAAcceptance





def users_kpi():
    total = User.objects.count()

    entrepreneurs = User.objects.filter(role="entrepreneur").count()
    investors = User.objects.filter(role="investor").count()

    today = now().date()
    last_7 = today - timedelta(days=7)

    today_new = User.objects.filter(created_at__date=today).count()
    week_new = User.objects.filter(created_at__date__gte=last_7).count()

    suspended = User.objects.filter(is_suspended=True).count()

    return {
        "total": total,
        "entrepreneurs": entrepreneurs,
        "investors": investors,
        "new_today": today_new,
        "new_last_7_days": week_new,
        "suspended": suspended
    }


def subscription_kpi():
    active = Subscription.objects.filter(status="active").count()

    by_plan = list(
        Subscription.objects
        .filter(status="active")
        .values("plan__name")
        .annotate(count=Count("id"))
    )

    today = now().date()

    revenue_today = Payment.objects.filter(
        status="success",
        created_at__date=today
    ).aggregate(total=Sum("amount"))["total"] or 0

    revenue_total = Payment.objects.filter(
        status="success"
    ).aggregate(total=Sum("amount"))["total"] or 0

    return {
        "active_subscriptions": active,
        "by_plan": by_plan,
        "revenue_today": revenue_today,
        "revenue_total": revenue_total
    }


def content_kpi():
    active_posts = Post.objects.filter(status="active").count()

    nda_uploaded = Post.objects.filter(nda_required=True).count()

    today = now().date()
    nda_accept_today = NDAAcceptance.objects.filter(
        accepted_at__date=today
    ).count()

    active_chats = ChatThread.objects.filter(is_frozen=False).count()

    return {
        "active_posts": active_posts,
        "nda_uploaded": nda_uploaded,
        "nda_accepted_today": nda_accept_today,
        "active_chats": active_chats
    }


from reports.models import Report

def reports_kpi():
    return {
        "open": Report.objects.filter(status="open").count(),
        "under_review": Report.objects.filter(status="under_review").count(),
        "resolved": Report.objects.filter(status="resolved").count()
    }
