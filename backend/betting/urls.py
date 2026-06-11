from django.urls import path
from . import views

urlpatterns = [
    path('betting/odds/<int:fixture_id>/', views.FixtureOddsView.as_view(), name='fixture-odds'),
    path('betting/place/', views.PlaceBetView.as_view(), name='place-bet'),
    path('betting/my-bets/', views.MyBetsView.as_view(), name='my-bets'),
    path('betting/resolve/<int:fixture_id>/', views.ResolveBetsView.as_view(), name='resolve-bets'),
]
