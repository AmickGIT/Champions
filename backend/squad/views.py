from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Squad, SquadPlayer
from .serializers import SquadSerializer, ChangeFormationSerializer, SwapPlayersSerializer
from .services import validate_formation, swap_players


class MySquadView(APIView):
    """Get the current user's squad."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            squad = Squad.objects.prefetch_related(
                'players__player__country'
            ).get(user=request.user)
        except Squad.DoesNotExist:
            return Response(
                {'error': 'You don\'t have a squad yet. Complete the draft first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SquadSerializer(squad)
        return Response(serializer.data)


class ChangeFormationView(APIView):
    """Change the user's squad formation."""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangeFormationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            squad = Squad.objects.get(user=request.user)
        except Squad.DoesNotExist:
            return Response({'error': 'Squad not found'}, status=404)

        new_formation = serializer.validated_data['formation']
        is_valid, error = validate_formation(new_formation, squad)

        if not is_valid:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        squad.formation = new_formation
        squad.save(update_fields=['formation'])

        return Response({
            'message': f'Formation changed to {new_formation}',
            'squad': SquadSerializer(squad).data
        })


class SwapPlayersView(APIView):
    """Swap two players between starter and bench."""
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = SwapPlayersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            squad = Squad.objects.get(user=request.user)
        except Squad.DoesNotExist:
            return Response({'error': 'Squad not found'}, status=404)

        success, error = swap_players(
            squad,
            serializer.validated_data['player1_id'],
            serializer.validated_data['player2_id']
        )

        if not success:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        squad.refresh_from_db()
        return Response({
            'message': 'Players swapped successfully',
            'squad': SquadSerializer(squad).data
        })


class UserSquadView(APIView):
    """View another user's squad (read-only)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            squad = Squad.objects.prefetch_related(
                'players__player__country'
            ).get(user_id=user_id)
        except Squad.DoesNotExist:
            return Response({'error': 'Squad not found'}, status=404)

        serializer = SquadSerializer(squad)
        return Response(serializer.data)
