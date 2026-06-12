"""
API-Football client for Champions.
Handles all communication with the API-Football v3 API.
"""
import requests
import logging
from datetime import datetime
from django.conf import settings
from .models import Country, Player, Fixture, PlayerMatchStats
from .scoring import POSITION_MAP

logger = logging.getLogger(__name__)


class APIFootballClient:
    """Client for the API-Football v3 API."""

    def __init__(self):
        self.base_url = settings.API_FOOTBALL_BASE_URL
        self.api_key = settings.API_FOOTBALL_KEY
        self.headers = {
            'x-apisports-key': self.api_key,
        }

    def _get(self, endpoint, params=None):
        """Make a GET request to the API."""
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            if data.get('errors'):
                logger.error(f"API errors: {data['errors']}")
                return None
            return data
        except requests.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None

    # ──────────────────────────────────────────────
    # Data Seeding (one-time operations)
    # ──────────────────────────────────────────────

    def fetch_and_seed_teams(self):
        """Fetch all World Cup 2026 teams and create Country records."""
        config = settings.GAME_CONFIG
        data = self._get('teams', {
            'league': config['WORLD_CUP_LEAGUE_ID'],
            'season': config['WORLD_CUP_SEASON'],
        })
        if not data:
            return []

        created = []
        for item in data.get('response', []):
            team = item['team']
            country, was_created = Country.objects.update_or_create(
                api_team_id=team['id'],
                defaults={
                    'name': team['name'],
                    'code': team.get('code', team['name'][:3].upper()),
                    'flag_url': team.get('logo', ''),
                }
            )
            if was_created:
                created.append(country.name)

        logger.info(f"Seeded {len(created)} countries")
        return created

    def fetch_and_seed_squad(self, team_api_id):
        """Fetch squad for a team and create Player records."""
        data = self._get('players/squads', {'team': team_api_id})
        if not data:
            return []

        try:
            country = Country.objects.get(api_team_id=team_api_id)
        except Country.DoesNotExist:
            logger.error(f"Country with api_team_id {team_api_id} not found")
            return []

        created = []
        for item in data.get('response', []):
            for player_data in item.get('players', []):
                # Map position
                pos = player_data.get('position', 'Attacker')
                position_map = {
                    'Goalkeeper': 'GK',
                    'Defender': 'DEF',
                    'Midfielder': 'MID',
                    'Attacker': 'FWD',
                }
                position = position_map.get(pos, 'MID')

                player, was_created = Player.objects.update_or_create(
                    api_player_id=player_data['id'],
                    defaults={
                        'name': player_data.get('name', 'Unknown'),
                        'photo_url': player_data.get('photo', ''),
                        'country': country,
                        'position': position,
                        'jersey_number': player_data.get('number'),
                    }
                )
                if was_created:
                    created.append(player.name)

        logger.info(f"Seeded {len(created)} players for {country.name}")
        return created

    def seed_all_squads(self):
        """Seed squads for all countries in the database."""
        countries = Country.objects.all()
        total = []
        for country in countries:
            players = self.fetch_and_seed_squad(country.api_team_id)
            total.extend(players)
        return total

    # ──────────────────────────────────────────────
    # Fixtures
    # ──────────────────────────────────────────────

    def fetch_and_sync_fixtures(self):
        """Fetch all World Cup 2026 fixtures and sync to DB."""
        config = settings.GAME_CONFIG
        data = self._get('fixtures', {
            'league': config['WORLD_CUP_LEAGUE_ID'],
            'season': config['WORLD_CUP_SEASON'],
        })
        if not data:
            return []

        synced = []
        for item in data.get('response', []):
            fix = item['fixture']
            teams = item['teams']
            goals = item['goals']
            league = item['league']

            try:
                home_team = Country.objects.get(api_team_id=teams['home']['id'])
                away_team = Country.objects.get(api_team_id=teams['away']['id'])
            except Country.DoesNotExist:
                logger.warning(f"Team not found for fixture {fix['id']}")
                continue

            # Map API status to our status
            status_map = {
                'NS': 'scheduled',    # Not Started
                'TBD': 'scheduled',
                '1H': 'live',
                'HT': 'live',
                '2H': 'live',
                'ET': 'live',
                'P': 'live',
                'FT': 'finished',
                'AET': 'finished',
                'PEN': 'finished',
                'PST': 'postponed',
                'CANC': 'cancelled',
                'ABD': 'cancelled',
            }
            short_status = fix.get('status', {}).get('short', 'NS')
            status = status_map.get(short_status, 'scheduled')

            fixture, _ = Fixture.objects.update_or_create(
                api_fixture_id=fix['id'],
                defaults={
                    'home_team': home_team,
                    'away_team': away_team,
                    'kick_off': fix['date'],
                    'status': status,
                    'home_score': goals.get('home'),
                    'away_score': goals.get('away'),
                    'round': league.get('round', ''),
                    'venue': fix.get('venue', {}).get('name', '') if fix.get('venue') else '',
                }
            )
            synced.append(fixture)

        logger.info(f"Synced {len(synced)} fixtures")
        return synced

    # ──────────────────────────────────────────────
    # Player Stats (post-match)
    # ──────────────────────────────────────────────

    def fetch_and_sync_player_stats(self, fixture_api_id):
        """Fetch player stats for a finished fixture and save to DB."""
        data = self._get('fixtures/players', {'fixture': fixture_api_id})
        if not data:
            return []

        try:
            fixture = Fixture.objects.get(api_fixture_id=fixture_api_id)
        except Fixture.DoesNotExist:
            logger.error(f"Fixture with api_id {fixture_api_id} not found in DB")
            return []

        created = []
        for team_data in data.get('response', []):
            for player_data in team_data.get('players', []):
                p = player_data['player']
                stats_list = player_data.get('statistics', [])
                if not stats_list:
                    continue
                s = stats_list[0]  # First (primary) statistics entry

                try:
                    player = Player.objects.get(api_player_id=p['id'])
                except Player.DoesNotExist:
                    logger.warning(f"Player {p['id']} ({p.get('name')}) not in DB, skipping")
                    continue

                games = s.get('games', {})
                goals_data = s.get('goals', {})
                passes = s.get('passes', {})
                tackles_data = s.get('tackles', {})
                duels = s.get('duels', {})
                dribbles = s.get('dribbles', {})
                fouls = s.get('fouls', {})
                cards = s.get('cards', {})
                penalty = s.get('penalty', {})
                shots = s.get('shots', {})

                stats, was_created = PlayerMatchStats.objects.update_or_create(
                    player=player,
                    fixture=fixture,
                    defaults={
                        'minutes_played': games.get('minutes') or 0,
                        'position_played': games.get('position', ''),
                        'rating': games.get('rating') if games.get('rating') else None,
                        'was_substitute': games.get('substitute', False),
                        'goals': goals_data.get('total') or 0,
                        'assists': goals_data.get('assists') or 0,
                        'goals_conceded': goals_data.get('conceded') or 0,
                        'saves': goals_data.get('saves') or 0,
                        'passes_total': passes.get('total') or 0,
                        'passes_key': passes.get('key') or 0,
                        'pass_accuracy': passes.get('accuracy') or '',
                        'tackles': tackles_data.get('total') or 0,
                        'interceptions': tackles_data.get('interceptions') or 0,
                        'blocks': tackles_data.get('blocks') or 0,
                        'duels_total': duels.get('total') or 0,
                        'duels_won': duels.get('won') or 0,
                        'dribbles_attempted': dribbles.get('attempts') or 0,
                        'dribbles_success': dribbles.get('success') or 0,
                        'shots_total': shots.get('total') or 0,
                        'shots_on_target': shots.get('on') or 0,
                        'fouls_drawn': fouls.get('drawn') or 0,
                        'fouls_committed': fouls.get('committed') or 0,
                        'yellow_cards': cards.get('yellow') or 0,
                        'red_cards': cards.get('red') or 0,
                        'penalties_scored': penalty.get('scored') or 0,
                        'penalties_missed': penalty.get('missed') or 0,
                        'penalties_saved': penalty.get('saved') or 0,
                        'penalties_won': 1 if penalty.get('won') else 0,
                    }
                )
                if was_created:
                    created.append(stats)

        logger.info(f"Synced {len(created)} player stats for fixture {fixture_api_id}")
        return created

    # ──────────────────────────────────────────────
    # Odds (pre-match)
    # ──────────────────────────────────────────────

    def fetch_and_sync_odds(self, fixture_api_id):
        """Fetch betting odds for a fixture."""
        from betting.models import BettingOdds

        data = self._get('odds', {'fixture': fixture_api_id})
        if not data:
            return None

        try:
            fixture = Fixture.objects.get(api_fixture_id=fixture_api_id)
        except Fixture.DoesNotExist:
            logger.error(f"Fixture {fixture_api_id} not found")
            return None

        results = []
        for response_item in data.get('response', []):
            for bookmaker in response_item.get('bookmakers', []):
                for bet in bookmaker.get('bets', []):
                    bet_id = bet.get('id')
                    bet_name = bet.get('name', '')

                    # We only care about Match Winner (id=1) and Exact Score (id=10)
                    if bet_id == 1:
                        bet_type = 'match_winner'
                    elif bet_id == 10:
                        bet_type = 'exact_score'
                    else:
                        continue

                    odds_obj, _ = BettingOdds.objects.update_or_create(
                        fixture=fixture,
                        bet_type=bet_type,
                        defaults={
                            'odds_data': bet.get('values', []),
                        }
                    )
                    results.append(odds_obj)

                # Only process first bookmaker
                break

        logger.info(f"Synced odds for fixture {fixture_api_id}")
        return results
