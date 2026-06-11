from django.urls import path
from . import views

urlpatterns = [
    # Public data
    path('countries/', views.CountryListView.as_view(), name='country-list'),
    path('players/', views.PlayerListView.as_view(), name='player-list'),
    path('players/<int:pk>/', views.PlayerDetailView.as_view(), name='player-detail'),
    path('fixtures/upcoming/', views.UpcomingFixturesView.as_view(), name='fixtures-upcoming'),
    path('fixtures/recent/', views.RecentFixturesView.as_view(), name='fixtures-recent'),
    path('fixtures/<int:pk>/', views.FixtureDetailView.as_view(), name='fixture-detail'),
    path('fixtures/<int:fixture_id>/stats/', views.FixturePlayerStatsView.as_view(), name='fixture-stats'),

    # Admin endpoints
    path('admin/sync-teams/', views.AdminSyncTeamsView.as_view(), name='admin-sync-teams'),
    path('admin/sync-squads/', views.AdminSyncSquadsView.as_view(), name='admin-sync-squads'),
    path('admin/sync-fixtures/', views.AdminSyncFixturesView.as_view(), name='admin-sync-fixtures'),
    path('admin/sync-stats/<int:fixture_api_id>/', views.AdminSyncPlayerStatsView.as_view(), name='admin-sync-stats'),
    path('admin/sync-odds/<int:fixture_api_id>/', views.AdminSyncOddsView.as_view(), name='admin-sync-odds'),
    path('admin/process-match/<int:fixture_id>/', views.AdminProcessMatchView.as_view(), name='admin-process-match'),
]
