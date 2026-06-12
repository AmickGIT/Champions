from rest_framework import serializers
from .models import Draft, DraftPick
from core.serializers import PlayerListSerializer


class DraftPickSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    player = PlayerListSerializer(read_only=True)

    class Meta:
        model = DraftPick
        fields = ['id', 'pick_number', 'username', 'user', 'player', 'picked_at']


class DraftSerializer(serializers.ModelSerializer):
    picks = DraftPickSerializer(many=True, read_only=True)

    class Meta:
        model = Draft
        fields = [
            'id', 'status', 'pick_order', 'current_pick_index',
            'time_per_pick_seconds', 'current_pick_deadline',
            'started_at', 'completed_at', 'created_at',
            'total_picks', 'picks_remaining', 'picks',
        ]


class StartDraftSerializer(serializers.Serializer):
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=2,
        max_length=10,
        help_text="List of user IDs to participate in the draft"
    )


class MakePickSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
