import uuid
from django.db import models
from accounts.models import User


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    post_type = models.CharField(max_length=20)
    title = models.CharField(max_length=60)

    category = models.CharField(max_length=50)
    stage = models.CharField(max_length=50)

    country = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    is_remote = models.BooleanField(default=False)

    short_description = models.CharField(max_length=200)

    status = models.CharField(max_length=20, default='active')
    visibility = models.CharField(max_length=30, default='verified_only')

    nda_required = models.BooleanField(default=True)

    post_valid_till = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'posts'


class EntrepreneurPostDetails(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    problem = models.TextField(null=True, blank=True)
    solution = models.TextField(null=True, blank=True)
    target_users = models.TextField(null=True, blank=True)

    funding_min = models.BigIntegerField(null=True, blank=True)
    funding_max = models.BigIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)

    use_of_funds = models.TextField(null=True, blank=True)
    investor_return = models.CharField(max_length=50, null=True, blank=True)

    founder_name = models.CharField(max_length=100, null=True, blank=True)
    founder_type = models.CharField(max_length=30, null=True, blank=True)
    team_size = models.IntegerField(null=True, blank=True)
    founder_background = models.CharField(max_length=50, null=True, blank=True)

    business_description = models.TextField(null=True, blank=True)

    pitch_deck_url = models.TextField(null=True, blank=True)
    website_url = models.TextField(null=True, blank=True)

    linkedin_url = models.TextField(null=True, blank=True)
    twitter_url = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'entrepreneur_post_details'



class InvestorPostDetails(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)

    investor_title = models.CharField(max_length=100, null=True, blank=True)
    investor_type = models.CharField(max_length=50, null=True, blank=True)

    preferred_location = models.CharField(max_length=100, null=True, blank=True)

    investment_min = models.BigIntegerField(null=True, blank=True)
    investment_max = models.BigIntegerField(null=True, blank=True)
    currency = models.CharField(max_length=10, null=True, blank=True)

    stage_preference = models.CharField(max_length=100, null=True, blank=True)
    industries = models.TextField(null=True, blank=True)

    investment_style = models.CharField(max_length=50, null=True, blank=True)
    expected_return = models.CharField(max_length=50, null=True, blank=True)
    investment_horizon = models.CharField(max_length=50, null=True, blank=True)

    value_addition = models.TextField(null=True, blank=True)
    past_experience = models.CharField(max_length=50, null=True, blank=True)

    founder_preference = models.CharField(max_length=50, null=True, blank=True)
    minimum_validation = models.CharField(max_length=50, null=True, blank=True)
    ticket_strategy = models.CharField(max_length=50, null=True, blank=True)

    linkedin_url = models.TextField(null=True, blank=True)
    website_url = models.TextField(null=True, blank=True)

    active_deal_status = models.CharField(max_length=30, null=True, blank=True)

    class Meta:
        db_table = 'investor_post_details'



class PostNDA(models.Model):
    post = models.OneToOneField(Post, on_delete=models.CASCADE)
    nda_file_url = models.TextField()
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'post_ndas'

class NDAAcceptance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        db_column="post_id"
    )
    viewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_column="viewer_id"
    )
    accepted_at = models.DateTimeField(auto_now_add=True)
    viewer_ip = models.GenericIPAddressField(null=True, blank=True)
    viewer_device = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "nda_acceptances"
        unique_together = ("post", "viewer")





class PostEngagement(models.Model):
    ACTION_CHOICES = (
        ("like", "Like"),
        ("save", "Save"),
        ("share", "Share"),
        ("view", "View"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="engagements"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_engagements"
    )
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_engagements"
        unique_together = ("post", "user", "action")

    def __str__(self):
        return f"{self.user_id} - {self.action}"




class PostReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(
        "Post",
        on_delete=models.CASCADE,
        related_name="reports"
    )
    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reported_posts"
    )
    reason = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "post_reports"
        ordering = ["-created_at"]



# class EntrepreneurPostDetails(models.Model):
#     post = models.OneToOneField(
#         Post,
#         on_delete=models.CASCADE,
#         related_name="entrepreneur_details"
#     )
# class InvestorPostDetails(models.Model):
#     post = models.OneToOneField(
#         Post,
#         on_delete=models.CASCADE,
#         related_name="investor_details"
#     )
