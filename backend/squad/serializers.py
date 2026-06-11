from rest_framework import serializers
from .models import Squad, SquadPlayer
from core.serializers import PlayerListSerializer


class SquadPlayerSerializer(serializers.ModelSerializer):
    player = PlayerListSerializer(read_only=True)

    class Meta:
        model = SquadPlayer
        fields = ['id', 'player', 'is_starter', 'position_slot']


class SquadSerializer(serializers.ModelSerializer):
    players = SquadPlayerSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    total_points = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Squad
        fields = ['id', 'username', 'formation', 'players', 'total_points', 'created_at', 'updated_at']


class ChangeFormationSerializer(serializers.Serializer):
    formation = serializers.CharField(max_length=10)

    def validate_formation(self, value):
        from django.conf import settings
        valid = settings.GAME_CONFIG['VALID_FORMATIONS']
        if value not in valid:
            raise serializers.ValidationError(f"Invalid formation. Choose from: {valid}")
        return value


class SwapPlayersSerializer(serializers.Serializer):
    player1_id = serializers.IntegerField()
    player2_id = serializers.IntegerField()

    def validate(self, data):
        if data['player1_id'] == data['player2_id']:
            raise serializers.ValidationError("Cannot swap a player with themselves")
        return data
