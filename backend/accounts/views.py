from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import UserProfile
from .serializers import (
    LeaderboardSerializer,
    RegisterSerializer,
    UserProfileSerializer,
)


class RegisterView(generics.CreateAPIView):
    """
    Register a new user account.

    Creates a new User and associated UserProfile (via signal).
    Returns the created user's username and email.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class ProfileView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's profile.

    Returns the full user profile including balance, points, and admin status.
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class LeaderboardView(generics.ListAPIView):
    """
    List all users ranked by total fantasy points (descending).

    Returns a leaderboard of all users with their points and balance.
    """

    serializer_class = LeaderboardSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = UserProfile.objects.select_related("user").order_by(
        "-total_points"
    )
