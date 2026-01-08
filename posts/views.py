import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from accounts.utils import get_user_from_token
from django.utils.timezone import now
from .models import (
    Post,
    EntrepreneurPostDetails,
    InvestorPostDetails,
    PostNDA,
    NDAAcceptance,
    PostEngagement,
    PostReport
)


from .models import NDAAcceptance


from django.core.paginator import Paginator
from django.utils.timezone import now
from accounts.utils import get_user_from_token
from .models import Post


from .models import Post, NDAAcceptance
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from accounts.utils import get_user_from_token
from django.db import IntegrityError
import json

from django.db.models import Count


from analytics.services import log_event, log_funnel
from analytics.models import AnalyticsChatMetric, AnalyticsPayment




@csrf_exempt
def create_post(request):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    if user.subscription_status != "active":
        return JsonResponse({"error": "Subscription inactive"}, status=403)

    # ---- COMMON POST ----
    post = Post.objects.create(
        user=user,
        post_type=user.role,
        title=data["title"],
        category=data["category"],
        stage=data["stage"],
        country=data.get("country"),
        city=data.get("city"),
        is_remote=data.get("is_remote", False),
        short_description=data["short_description"],
        nda_required=data.get("nda_required", True),
        post_valid_till=data.get("post_valid_till")
    )

    # ---- ENTREPRENEUR POST ----
    if user.role == "entrepreneur":
        required_fields = [
            "problem", "solution", "target_users",
            "funding_min", "funding_max", "currency",
            "use_of_funds", "investor_return",
            "founder_name", "founder_type",
            "team_size", "founder_background",
            "business_description"
        ]

        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"Missing field: {field}"},
                    status=400
                )

        EntrepreneurPostDetails.objects.create(
            post=post,
            problem=data["problem"],
            solution=data["solution"],
            target_users=data["target_users"],
            funding_min=data["funding_min"],
            funding_max=data["funding_max"],
            currency=data["currency"],
            use_of_funds=data["use_of_funds"],
            investor_return=data["investor_return"],
            founder_name=data["founder_name"],
            founder_type=data["founder_type"],
            team_size=data["team_size"],
            founder_background=data["founder_background"],
            business_description=data["business_description"],
            pitch_deck_url=data.get("pitch_deck_url"),
            website_url=data.get("website_url"),
            linkedin_url=data.get("linkedin_url"),
            twitter_url=data.get("twitter_url"),
        )

    # ---- INVESTOR POST ----
    elif user.role == "investor":
        required_fields = [
            "investor_title", "investor_type",
            "preferred_location",
            "investment_min", "investment_max", "currency",
            "stage_preference", "industries",
            "investment_style", "expected_return",
            "investment_horizon",
            "value_addition", "past_experience",
            "founder_preference", "minimum_validation",
            "ticket_strategy", "active_deal_status"
        ]

        for field in required_fields:
            if field not in data:
                return JsonResponse(
                    {"error": f"Missing field: {field}"},
                    status=400
                )

        InvestorPostDetails.objects.create(
            post=post,
            investor_title=data["investor_title"],
            investor_type=data["investor_type"],
            preferred_location=data["preferred_location"],
            investment_min=data["investment_min"],
            investment_max=data["investment_max"],
            currency=data["currency"],
            stage_preference=data["stage_preference"],
            industries=data["industries"],
            investment_style=data["investment_style"],
            expected_return=data["expected_return"],
            investment_horizon=data["investment_horizon"],
            value_addition=data["value_addition"],
            past_experience=data["past_experience"],
            founder_preference=data["founder_preference"],
            minimum_validation=data["minimum_validation"],
            ticket_strategy=data["ticket_strategy"],
            active_deal_status=data["active_deal_status"]
        )

    # ---- NDA ----
    if data.get("nda_required") and data.get("nda_file_url"):
        PostNDA.objects.create(
            post=post,
            nda_file_url=data["nda_file_url"]
        )

    return JsonResponse({
        "message": "Post created successfully",
        "post_id": str(post.id)
    })




def feed(request):
    user = get_user_from_token(request)

    posts = Post.objects.filter(
        status='active'
    ).exclude(user=user).order_by('-created_at')

    data = []
    for p in posts:
        data.append({
            "post_id": str(p.id),
            "title": p.title,
            "stage": p.stage,
            "category": p.category,
            "location": "Remote" if p.is_remote else f"{p.city}, {p.country}",
            "short_description": p.short_description,
            "nda_required": p.nda_required
        })

    return JsonResponse(data, safe=False)



@csrf_exempt
def accept_nda(request, post_id):
    user = get_user_from_token(request)
    post = Post.objects.get(id=post_id)

    if not post.nda_required:
        return JsonResponse({"message": "NDA not required"})

    NDAAcceptance.objects.get_or_create(
        post=post,
        viewer=user,
        defaults={
            "viewer_ip": request.META.get("REMOTE_ADDR"),
            "viewer_device": request.META.get("HTTP_USER_AGENT")
        }
    )

    # 📊 ANALYTICS
    log_event(
        user_id=user.id,
        role=user.role,
        event_type="nda_accept",
        target_type="post",
        target_id=post.id
    )

    log_funnel(user.id, user.role, "nda_accepted")

    return JsonResponse({"message": "NDA accepted"})

    


def view_post(request, post_id):
    user = get_user_from_token(request)
    post = Post.objects.get(id=post_id)
    # 📊 ANALYTICS: Post View
    log_event(
        user_id=user.id,
        role=user.role,
        event_type="post_view",
        target_type="post",
        target_id=post.id,
        ip=request.META.get("REMOTE_ADDR"),
        device=request.META.get("HTTP_USER_AGENT")
)

    # ---- NDA CHECK ----
    if post.nda_required:
        accepted = NDAAcceptance.objects.filter(
            post=post,
            viewer=user
        ).exists()

        if not accepted:
            return JsonResponse(
                {"error": "NDA required"},
                status=403
            )

    # ---- ENTREPRENEUR POST ----
    if post.post_type == "entrepreneur":
        d = EntrepreneurPostDetails.objects.filter(post=post).first()

        if not d:
            return JsonResponse(
                {"error": "Entrepreneur details not found"},
                status=404
            )

        details = {
            "problem": d.problem,
            "solution": d.solution,
            "target_users": d.target_users,
            "funding_min": d.funding_min,
            "funding_max": d.funding_max,
            "currency": d.currency,
            "use_of_funds": d.use_of_funds,
            "investor_return": d.investor_return,
            "founder_name": d.founder_name,
            "founder_type": d.founder_type,
            "team_size": d.team_size,
            "founder_background": d.founder_background,
            "business_description": d.business_description,
            "pitch_deck_url": d.pitch_deck_url,
            "website_url": d.website_url,
            "linkedin_url": d.linkedin_url,
            "twitter_url": d.twitter_url,
        }

    # ---- INVESTOR POST ----
    elif post.post_type == "investor":
        d = InvestorPostDetails.objects.filter(post=post).first()

        if not d:
            return JsonResponse(
                {"error": "Investor details not found"},
                status=404
            )

        details = {
            "investor_title": d.investor_title,
            "investor_type": d.investor_type,
            "preferred_location": d.preferred_location,
            "investment_min": d.investment_min,
            "investment_max": d.investment_max,
            "currency": d.currency,
            "stage_preference": d.stage_preference,
            "industries": d.industries,
            "investment_style": d.investment_style,
            "expected_return": d.expected_return,
            "investment_horizon": d.investment_horizon,
            "value_addition": d.value_addition,
            "past_experience": d.past_experience,
            "founder_preference": d.founder_preference,
            "minimum_validation": d.minimum_validation,
            "ticket_strategy": d.ticket_strategy,
            "active_deal_status": d.active_deal_status,
        }

    else:
        return JsonResponse(
            {"error": "Invalid post type"},
            status=400
        )

    return JsonResponse({
        "post": {
            "id": str(post.id),
            "title": post.title,
            "category": post.category,
            "stage": post.stage,
            "location": "Remote" if post.is_remote else f"{post.city}, {post.country}",
            "nda_required": post.nda_required,
        },
        "details": details
    })


from django.views.decorators.csrf import csrf_exempt
def discovery_feed(request):
    user = get_user_from_token(request)

    # Role-based opposite feed
    target_post_type = (
        "investor" if user.role == "entrepreneur" else "entrepreneur"
    )

    queryset = Post.objects.filter(
        post_type=target_post_type,
        status="active"
    ).exclude(
        post_valid_till__lt=now().date()
    ).order_by("-created_at")

    # Pagination
    page_number = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("limit", 10))

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)

    results = []
    for post in page:
        results.append({
            "post_id": str(post.id),
            "title": post.title,
            "category": post.category,
            "stage": post.stage,
            "location": (
                "Remote"
                if post.is_remote
                else f"{post.city}, {post.country}"
            ),
            "short_description": post.short_description,
            "nda_required": post.nda_required,
        })

    return JsonResponse({
        "page": page_number,
        "total_pages": paginator.num_pages,
        "total_posts": paginator.count,
        "results": results
    })


def discovery_with_filters(request):
    user = get_user_from_token(request)

    target_post_type = (
        "investor" if user.role == "entrepreneur" else "entrepreneur"
    )

    queryset = Post.objects.filter(
        post_type=target_post_type,
        status="active"
    ).exclude(
        post_valid_till__lt=now().date()
    )

    # ---- Filters ----
    category = request.GET.get("category")
    stage = request.GET.get("stage")
    country = request.GET.get("country")
    city = request.GET.get("city")

    if category:
        queryset = queryset.filter(category__iexact=category)

    if stage:
        queryset = queryset.filter(stage__iexact=stage)

    if country:
        queryset = queryset.filter(country__iexact=country)

    if city:
        queryset = queryset.filter(city__iexact=city)

    queryset = queryset.order_by("-created_at")

    # Pagination
    page_number = int(request.GET.get("page", 1))
    page_size = int(request.GET.get("limit", 10))

    paginator = Paginator(queryset, page_size)
    page = paginator.get_page(page_number)

    results = [{
        "post_id": str(p.id),
        "title": p.title,
        "category": p.category,
        "stage": p.stage,
        "location": (
            "Remote"
            if p.is_remote
            else f"{p.city}, {p.country}"
        ),
        "short_description": p.short_description,
        "nda_required": p.nda_required,
    } for p in page]

    return JsonResponse({
        "page": page_number,
        "total_pages": paginator.num_pages,
        "results": results
    })


@csrf_exempt
def engage_post(request, post_id):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    action = data.get("action")  # like / save / share

    if action not in ["like", "save", "share"]:
        return JsonResponse({"error": "Invalid action"}, status=400)

    try:
        PostEngagement.objects.create(
            post_id=post_id,
            user_id=user.id,
            action=action
        )
        return JsonResponse({"message": f"{action} added"})
    except IntegrityError:
        # Toggle for like/save
        PostEngagement.objects.filter(
            post_id=post_id,
            user_id=user.id,
            action=action
        ).delete()
        return JsonResponse({"message": f"{action} removed"})


@csrf_exempt
def track_view(request, post_id):
    user = get_user_from_token(request)

    PostEngagement.objects.get_or_create(
        post_id=post_id,
        user_id=user.id,
        action="view"
    )

    return JsonResponse({"message": "View recorded"})



@csrf_exempt
def report_post(request, post_id):
    user = get_user_from_token(request)
    data = json.loads(request.body)

    PostReport.objects.create(
        post_id=post_id,
        reporter_id=user.id,
        reason=data["reason"],
        description=data.get("description", "")
    )

    return JsonResponse({"message": "Report submitted"})


def post_engagement_counts(request, post_id):
    data = PostEngagement.objects.filter(
        post_id=post_id
    ).values("action").annotate(count=Count("id"))

    return JsonResponse(list(data), safe=False)
