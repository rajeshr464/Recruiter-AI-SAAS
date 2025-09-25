"""
URL configuration for recruiter_ai_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from core.views import *
from core.views import *

router = DefaultRouter()
router.register("tenants", TenantViewSet)
router.register("clients", ClientViewSet)
router.register("recruiters", RecruiterViewSet)
router.register("recruiter-ai", RecruiterAIViewSet)
router.register("candidates", CandidateViewSet)
router.register("jobs", JobViewSet)
router.register("submissions", SubmissionViewSet)
router.register("interviews", InterviewViewSet)
router.register("offers", OfferViewSet)
router.register("ai-learning-logs", AILearningLogViewSet)
router.register("tasks", TaskViewSet, basename="tasks")
router.register("reports", ReportViewSet, basename="reports")
router.register("settings", SettingViewSet, basename="settings")
router.register("help", HelpViewSet, basename="help")

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("login/", LoginView.as_view(), name="login"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("ai/", include("ai_engine.urls")),
    path("add_candidate/", CandidateIntakeView.as_view(), name="add_candidate"),
    path("candidates/", CandidateListView.as_view(), name="candidate_list"),
    path("parse_resume/", ParseResumeView.as_view(), name="parse_resume"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
