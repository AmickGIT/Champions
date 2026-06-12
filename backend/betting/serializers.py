from rest_framework import serializers
from .models import BettingOdds, Bet
from core.serializers import FixtureSerializer

class BettingOddsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BettingOdds
        fields = ['fixture_id', 'bet_type', 'odds_data', 'fetched_at']

class PlaceBetSerializer(serializers.Serializer):
    fixture_id = serializers.IntegerField()
    bet_type = serializers.CharField(max_length=50)
    prediction = serializers.CharField(max_length=50)
    stake = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=0.01)

class BetSerializer(serializers.ModelSerializer):
    fixture = FixtureSerializer(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Bet
        fields = '__all__'
