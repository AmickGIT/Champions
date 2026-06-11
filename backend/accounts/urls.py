from django.urls import path

from .views import LeaderboardView, ProfileView, RegisterView

urlpatterns = [
    path("api/auth/register/", RegisterView.as_view(), name="register"),
    path("api/auth/profile/", ProfileView.as_view(), name="profile"),
    path("api/leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
]
