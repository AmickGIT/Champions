from django.contrib import admin
from .models import BettingOdds, Bet

@admin.register(BettingOdds)
class BettingOddsAdmin(admin.ModelAdmin):
    list_display = ['fixture', 'bet_type', 'fetched_at']
    list_filter = ['bet_type']

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ['user', 'fixture', 'bet_type', 'prediction', 'odds', 'stake', 'status', 'payout']
    list_filter = ['status', 'bet_type']
    search_fields = ['user__username', 'fixture__home_team__name', 'fixture__away_team__name']
