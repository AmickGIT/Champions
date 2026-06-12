from django.contrib import admin
from .models import Transaction, SilentAuction, AuctionBid

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'type', 'amount', 'created_at']
    list_filter = ['type']
    search_fields = ['user__username', 'description']

@admin.register(SilentAuction)
class SilentAuctionAdmin(admin.ModelAdmin):
    list_display = ['country', 'status', 'opens_at', 'closes_at']
    list_filter = ['status']
    search_fields = ['country__name']

@admin.register(AuctionBid)
class AuctionBidAdmin(admin.ModelAdmin):
    list_display = ['auction', 'user', 'target_player', 'bid_amount', 'placed_at']
    search_fields = ['user__username', 'target_player__name']
