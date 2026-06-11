from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import Draft, DraftPick
from core.models import Player
from .serializers import (
    DraftSerializer, DraftPickSerializer, StartDraftSerializer,
    MakePickSerializer
)
from .services import DraftService


class DraftStateView(APIView):
    """
    Get the current state of the draft.
    Frontend should poll this endpoint every 2-3 seconds during active drafts.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Find the active draft, or most recent waiting/completed
        draft = Draft.objects.filter(status__in=['active', 'waiting']).order_by('-created_at').first()
        if not draft:
            draft = Draft.objects.order_by('-created_at').first()
            
        if not draft:
            return Response({'error': 'No drafts found'}, status=404)

        state = DraftService.get_draft_state(draft)
        return Response(state)


class StartDraftView(APIView):
    """Admin: Start a new draft session."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = StartDraftSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            draft = DraftService.start_draft(
                request.user,
                serializer.validated_data['participant_ids']
            )
            return Response(
                DraftSerializer(draft).data,
                status=status.HTTP_201_CREATED
            )
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MakePickView(APIView):
    """Make a draft pick."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MakePickSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        draft = Draft.objects.filter(status='active').order_by('-created_at').first()
        if not draft:
            return Response({'error': 'No active draft found'}, status=status.HTTP_404_NOT_FOUND)

        player = get_object_or_404(Player, id=serializer.validated_data['player_id'])

        pick, error = DraftService.make_pick(draft, request.user, player)

        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            DraftPickSerializer(pick).data,
            status=status.HTTP_201_CREATED
        )


class DraftPicksView(APIView):
    """List all picks for the current draft."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        draft = Draft.objects.order_by('-created_at').first()
        if not draft:
            return Response({'error': 'No drafts found'}, status=404)

        picks = DraftPick.objects.filter(draft=draft).order_by('pick_number')
        serializer = DraftPickSerializer(picks, many=True)
        return Response(serializer.data)


class AutoPickView(APIView):
    """Admin: Trigger auto-pick for current turn."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        draft = Draft.objects.filter(status='active').first()
        if not draft:
            return Response({'error': 'No active draft'}, status=404)

        pick, error = DraftService.auto_pick(draft)
        
        if error:
            return Response({'error': error}, status=400)
            
        return Response(
            DraftPickSerializer(pick).data,
            status=status.HTTP_201_CREATED
        )
