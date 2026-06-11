from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.utils import timezone
from .models import Country, Player, Fixture, PlayerMatchStats
from .serializers import (
    CountrySerializer, PlayerSerializer, PlayerListSerializer,
    FixtureSerializer, PlayerMatchStatsSerializer,
)
from .api_client import APIFootballClient
from .scoring import process_fixture_points


class CountryListView(generics.ListAPIView):
    """List all World Cup countries."""
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    pagination_class = None


class PlayerListView(generics.ListAPIView):
    """List all players with filtering."""
    serializer_class = PlayerListSerializer

    def get_queryset(self):
        qs = Player.objects.select_related('country', 'owner').all()

        # Filter by position
        position = self.request.query_params.get('position')
        if position:
            qs = qs.filter(position=position.upper())

        # Filter by country
        country_id = self.request.query_params.get('country')
        if country_id:
            qs = qs.filter(country_id=country_id)

        # Filter available only
        available = self.request.query_params.get('available')
        if available and available.lower() == 'true':
            qs = qs.filter(owner__isnull=True)

        # Search by name
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(name__icontains=search)

        return qs


class PlayerDetailView(generics.RetrieveAPIView):
    """Get detailed player info."""
    queryset = Player.objects.select_related('country', 'owner').all()
    serializer_class = PlayerSerializer


class UpcomingFixturesView(generics.ListAPIView):
    """List upcoming scheduled fixtures."""
    serializer_class = FixtureSerializer
    pagination_class = None

    def get_queryset(self):
        return Fixture.objects.filter(
            status='scheduled',
            kick_off__gte=timezone.now()
        ).select_related('home_team', 'away_team').order_by('kick_off')[:20]


class RecentFixturesView(generics.ListAPIView):
    """List recently finished fixtures."""
    serializer_class = FixtureSerializer
    pagination_class = None

    def get_queryset(self):
        return Fixture.objects.filter(
            status='finished'
        ).select_related('home_team', 'away_team').order_by('-kick_off')[:20]


class FixtureDetailView(generics.RetrieveAPIView):
    """Get detailed fixture info."""
    queryset = Fixture.objects.select_related('home_team', 'away_team').all()
    serializer_class = FixtureSerializer


class FixturePlayerStatsView(generics.ListAPIView):
    """Get all player stats for a specific fixture."""
    serializer_class = PlayerMatchStatsSerializer
    pagination_class = None

    def get_queryset(self):
        fixture_id = self.kwargs['fixture_id']
        return PlayerMatchStats.objects.filter(
            fixture_id=fixture_id
        ).select_related('player', 'player__country', 'fixture')


# ──────────────────────────────────────────────
# Admin Endpoints
# ──────────────────────────────────────────────

class AdminSyncTeamsView(APIView):
    """Admin: Seed teams from API-Football."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        client = APIFootballClient()
        created = client.fetch_and_seed_teams()
        return Response({
            'message': f'Seeded {len(created)} teams',
            'teams': created,
        })


class AdminSyncSquadsView(APIView):
    """Admin: Seed all player squads from API-Football."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        team_id = request.data.get('team_id')
        client = APIFootballClient()

        if team_id:
            created = client.fetch_and_seed_squad(int(team_id))
        else:
            created = client.seed_all_squads()

        return Response({
            'message': f'Seeded {len(created)} players',
            'players': created[:50],  # Limit response size
        })


class AdminSyncFixturesView(APIView):
    """Admin: Sync fixtures from API-Football."""
    permission_classes = [IsAdminUser]

    def post(self, request):
        client = APIFootballClient()
        synced = client.fetch_and_sync_fixtures()
        return Response({
            'message': f'Synced {len(synced)} fixtures',
        })


class AdminSyncPlayerStatsView(APIView):
    """Admin: Fetch player stats for a specific fixture."""
    permission_classes = [IsAdminUser]

    def post(self, request, fixture_api_id):
        client = APIFootballClient()
        stats = client.fetch_and_sync_player_stats(fixture_api_id)
        return Response({
            'message': f'Synced {len(stats)} player stats',
        })


class AdminProcessMatchView(APIView):
    """Admin: Calculate fantasy points for a finished fixture."""
    permission_classes = [IsAdminUser]

    def post(self, request, fixture_id):
        try:
            fixture = Fixture.objects.get(id=fixture_id)
        except Fixture.DoesNotExist:
            return Response({'error': 'Fixture not found'}, status=404)

        if fixture.status != 'finished':
            return Response({'error': 'Fixture is not finished yet'}, status=400)

        if fixture.stats_processed:
            return Response({'error': 'Stats already processed for this fixture'}, status=400)

        process_fixture_points(fixture)
        return Response({
            'message': f'Processed fantasy points for {fixture}',
        })


class AdminSyncOddsView(APIView):
    """Admin: Fetch odds for a specific fixture."""
    permission_classes = [IsAdminUser]

    def post(self, request, fixture_api_id):
        client = APIFootballClient()
        results = client.fetch_and_sync_odds(fixture_api_id)
        return Response({
            'message': f'Synced odds for fixture {fixture_api_id}',
            'count': len(results) if results else 0,
        })
