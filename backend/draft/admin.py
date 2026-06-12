from django.contrib import admin
from .models import Draft, DraftPick

@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'current_pick_index', 'started_at']
    list_filter = ['status']


@admin.register(DraftPick)
class DraftPickAdmin(admin.ModelAdmin):
    list_display = ['pick_number', 'draft', 'user', 'player', 'picked_at']
    search_fields = ['user__username', 'player__name']
    raw_id_fields = ['player', 'user']
