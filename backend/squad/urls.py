from django.urls import path
from . import views

urlpatterns = [
    path('squad/', views.MySquadView.as_view(), name='my-squad'),
    path('squad/formation/', views.ChangeFormationView.as_view(), name='change-formation'),
    path('squad/swap/', views.SwapPlayersView.as_view(), name='swap-players'),
    path('squad/user/<int:user_id>/', views.UserSquadView.as_view(), name='user-squad'),
]
