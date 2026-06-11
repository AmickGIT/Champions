from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import Bet
from core.models import Fixture
from .serializers import PlaceBetSerializer, BetSerializer
from .services import BettingService


class FixtureOddsView(APIView):
    """Get odds for a specific fixture."""
    permission_classes = [IsAuthenticated]

    def get(self, request, fixture_id):
        fixture = get_object_or_404(Fixture, id=fixture_id)
        odds = BettingService.get_odds_for_fixture(fixture)
        
        return Response({
            'fixture_id': fixture_id,
            'odds': odds
        })


class PlaceBetView(APIView):
    """Place a bet."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PlaceBetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        fixture = get_object_or_404(Fixture, id=data['fixture_id'])
        
        bet, error = BettingService.place_bet(
            user=request.user,
            fixture=fixture,
            bet_type=data['bet_type'],
            prediction=data['prediction'],
            stake=data['stake']
        )
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(BetSerializer(bet).data, status=status.HTTP_201_CREATED)


class MyBetsView(generics.ListAPIView):
    """List all bets for the current user."""
    serializer_class = BetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user).select_related(
            'fixture', 'fixture__home_team', 'fixture__away_team'
        ).order_by('-placed_at')


class ResolveBetsView(APIView):
    """Admin: Resolve all bets for a given fixture."""
    permission_classes = [IsAdminUser]

    def post(self, request, fixture_id):
        fixture = get_object_or_404(Fixture, id=fixture_id)
        success, message = BettingService.resolve_bets_for_fixture(fixture)
        
        if not success:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message': message})
