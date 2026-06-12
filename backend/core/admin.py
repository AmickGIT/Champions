from django.contrib import admin
from .models import Country, Player, Fixture, PlayerMatchStats


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'api_team_id', 'group', 'is_eliminated']
    list_filter = ['is_eliminated', 'group']
    search_fields = ['name', 'code']


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'position', 'market_value', 'total_fantasy_points', 'owner', 'is_available']
    list_filter = ['position', 'country', 'is_available']
    search_fields = ['name', 'country__name']
    raw_id_fields = ['owner', 'country']


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'kick_off', 'status', 'home_score', 'away_score', 'round', 'stats_processed']
    list_filter = ['status', 'stats_processed', 'round']
    search_fields = ['home_team__name', 'away_team__name']


@admin.register(PlayerMatchStats)
class PlayerMatchStatsAdmin(admin.ModelAdmin):
    list_display = ['player', 'fixture', 'minutes_played', 'goals', 'assists', 'fantasy_points']
    list_filter = ['fixture']
    search_fields = ['player__name']
    raw_id_fields = ['player', 'fixture']
