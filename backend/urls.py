from django.contrib import admin
from django.urls import path, include


from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.urls')),
    path("api/subscriptions/", include("subscriptions.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/adminpanel/", include("adminpanel.urls")),
    path("api/token/refresh/", TokenRefreshView.as_view()),
    path("api/chat/", include("chat.urls")),
    path("api/reports/", include("reports.urls")),
   


]
# path('api/admin/', include('adminpanel.urls')),
