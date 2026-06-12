from django.urls import path
from . import views

urlpatterns = [
    path('draft/state/', views.DraftStateView.as_view(), name='draft-state'),
    path('draft/start/', views.StartDraftView.as_view(), name='draft-start'),
    path('draft/pick/', views.MakePickView.as_view(), name='draft-pick'),
    path('draft/picks/', views.DraftPicksView.as_view(), name='draft-picks'),
    path('draft/auto-pick/', views.AutoPickView.as_view(), name='draft-auto-pick'),
]
