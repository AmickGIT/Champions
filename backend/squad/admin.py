from django.contrib import admin
from .models import Squad, SquadPlayer


@admin.register(Squad)
class SquadAdmin(admin.ModelAdmin):
    list_display = ['user', 'formation', 'created_at']
    search_fields = ['user__username']


@admin.register(SquadPlayer)
class SquadPlayerAdmin(admin.ModelAdmin):
    list_display = ['squad', 'player', 'is_starter', 'position_slot']
    list_filter = ['is_starter']
    search_fields = ['player__name', 'squad__user__username']
    raw_id_fields = ['squad', 'player']
