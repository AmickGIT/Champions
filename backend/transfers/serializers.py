from rest_framework import serializers
from .models import Transaction, SilentAuction, AuctionBid
from core.serializers import CountrySerializer

class TransactionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'username', 'type', 'amount', 'description', 'created_at']

class BuyPlayerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    drop_player_id = serializers.IntegerField(required=False, allow_null=True)

class SellPlayerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()

class SilentAuctionSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)

    class Meta:
        model = SilentAuction
        fields = ['id', 'country', 'status', 'opens_at', 'closes_at', 'created_at']

class AuctionBidSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuctionBid
        fields = ['id', 'auction', 'user', 'target_player', 'bid_amount', 'placed_at']

class PlaceAuctionBidSerializer(serializers.Serializer):
    target_player_id = serializers.IntegerField()
    bid_amount = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)
