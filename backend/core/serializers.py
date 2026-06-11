from rest_framework import serializers
from .models import Country, Player, Fixture, PlayerMatchStats


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'flag_url', 'api_team_id', 'is_eliminated', 'group']


class PlayerSerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True, default=None)

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'photo_url', 'api_player_id', 'country',
            'position', 'market_value', 'total_fantasy_points',
            'owner', 'owner_username', 'is_available', 'jersey_number',
        ]


class PlayerListSerializer(serializers.ModelSerializer):
    """Lighter serializer for listing many players."""
    country_name = serializers.CharField(source='country.name', read_only=True)
    country_code = serializers.CharField(source='country.code', read_only=True)
    country_flag = serializers.URLField(source='country.flag_url', read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True, default=None)

    class Meta:
        model = Player
        fields = [
            'id', 'name', 'photo_url', 'position',
            'country_name', 'country_code', 'country_flag',
            'market_value', 'total_fantasy_points',
            'owner', 'owner_username', 'is_available', 'jersey_number',
        ]


class FixtureSerializer(serializers.ModelSerializer):
    home_team = CountrySerializer(read_only=True)
    away_team = CountrySerializer(read_only=True)
    result = serializers.CharField(read_only=True)
    score_string = serializers.CharField(read_only=True)

    class Meta:
        model = Fixture
        fields = [
            'id', 'api_fixture_id', 'home_team', 'away_team',
            'kick_off', 'status', 'home_score', 'away_score',
            'round', 'venue', 'stats_processed', 'result', 'score_string',
        ]


class PlayerMatchStatsSerializer(serializers.ModelSerializer):
    player = PlayerListSerializer(read_only=True)
    fixture = FixtureSerializer(read_only=True)

    class Meta:
        model = PlayerMatchStats
        fields = '__all__'
