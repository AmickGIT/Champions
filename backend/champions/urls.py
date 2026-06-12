"""
URL configuration for Champions project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Auth
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # App URLs
    path('api/', include('accounts.urls')),
    path('api/', include('core.urls')),
    path('api/', include('squad.urls')),
    path('api/', include('draft.urls')),
    path('api/', include('betting.urls')),
    path('api/', include('transfers.urls')),
]
