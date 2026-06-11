"""
Fantasy Points Scoring Engine for Champions.

Calculates fantasy points based on player match statistics,
using position-specific scoring rules derived from API-Football data.
"""
from decimal import Decimal


# ──────────────────────────────────────────────────────
# Scoring Configuration
# ──────────────────────────────────────────────────────

SCORING_TABLE = {
    # ── Universal Events ──
    'minutes_played_any': 1,       # Played any minutes (>0)
    'minutes_played_60_plus': 1,   # Played 60+ minutes (bonus on top)
    'goal_gk_def': 6,             # Goal by GK or DEF
    'goal_mid': 5,                # Goal by MID
    'goal_fwd': 4,                # Goal by FWD
    'assist': 3,
    'yellow_card': -1,
    'red_card': -3,
    'penalty_miss': -2,

    # ── Position-Specific ──
    'clean_sheet_gk_def': 4,      # GK, DEF: team conceded 0 & played 60+ min
    'clean_sheet_mid': 1,         # MID: team conceded 0 & played 60+ min
    'saves_per_3': 1,             # GK: per 3 saves
    'penalty_saved': 5,           # GK: each penalty saved
    'tackles_per_2': 1,           # DEF, MID: per 2 tackles
    'interceptions_per_3': 1,     # DEF, MID: per 3 interceptions
    'passes_30_70pct': 1,         # MID: 30+ passes with 70%+ accuracy
    'key_passes_per_2': 1,        # MID, FWD: per 2 key passes
    'dribbles_per_2': 1,          # FWD, MID: per 2 successful dribbles
    'duels_won_per_3': 1,         # DEF: per 3 duels won
    'shots_on_target_per_2': 1,   # FWD: per 2 shots on target
    'penalty_won': 2,             # Any: each penalty won
}

# Map API position codes to our standard positions
POSITION_MAP = {
    'G': 'GK',
    'D': 'DEF',
    'M': 'MID',
    'F': 'FWD',
}


def calculate_fantasy_points(stats) -> Decimal:
    """
    Calculate fantasy points for a PlayerMatchStats object.

    Args:
        stats: PlayerMatchStats instance with all stat fields populated.

    Returns:
        Decimal: Total fantasy points earned.
    """
    points = Decimal('0')
    position = stats.player.position  # GK, DEF, MID, FWD

    # ── Minutes Played ──
    if stats.minutes_played > 0:
        points += SCORING_TABLE['minutes_played_any']
    if stats.minutes_played >= 60:
        points += SCORING_TABLE['minutes_played_60_plus']

    # ── Goals (position-dependent value) ──
    if stats.goals > 0:
        if position in ('GK', 'DEF'):
            points += stats.goals * SCORING_TABLE['goal_gk_def']
        elif position == 'MID':
            points += stats.goals * SCORING_TABLE['goal_mid']
        else:  # FWD
            points += stats.goals * SCORING_TABLE['goal_fwd']

    # ── Assists ──
    points += stats.assists * SCORING_TABLE['assist']

    # ── Cards ──
    points += stats.yellow_cards * SCORING_TABLE['yellow_card']
    points += stats.red_cards * SCORING_TABLE['red_card']

    # ── Penalty Miss ──
    points += stats.penalties_missed * SCORING_TABLE['penalty_miss']

    # ── Penalty Won ──
    points += stats.penalties_won * SCORING_TABLE['penalty_won']

    # ── Clean Sheet (only if played 60+ minutes) ──
    if stats.minutes_played >= 60 and stats.goals_conceded == 0:
        if position in ('GK', 'DEF'):
            points += SCORING_TABLE['clean_sheet_gk_def']
        elif position == 'MID':
            points += SCORING_TABLE['clean_sheet_mid']

    # ── GK-Specific ──
    if position == 'GK':
        # Saves: 1 point per 3 saves
        points += (stats.saves // 3) * SCORING_TABLE['saves_per_3']
        # Penalty saved
        points += stats.penalties_saved * SCORING_TABLE['penalty_saved']

    # ── DEF/MID: Tackles ──
    if position in ('DEF', 'MID'):
        points += (stats.tackles // 2) * SCORING_TABLE['tackles_per_2']

    # ── DEF/MID: Interceptions ──
    if position in ('DEF', 'MID'):
        points += (stats.interceptions // 3) * SCORING_TABLE['interceptions_per_3']

    # ── MID: Pass bonus (30+ passes with 70%+ accuracy) ──
    if position == 'MID':
        accuracy_pct = _parse_accuracy(stats.pass_accuracy)
        if stats.passes_total >= 30 and accuracy_pct >= 70:
            points += SCORING_TABLE['passes_30_70pct']

    # ── MID/FWD: Key passes ──
    if position in ('MID', 'FWD'):
        points += (stats.passes_key // 2) * SCORING_TABLE['key_passes_per_2']

    # ── FWD/MID: Dribbles ──
    if position in ('FWD', 'MID'):
        points += (stats.dribbles_success // 2) * SCORING_TABLE['dribbles_per_2']

    # ── DEF: Duels won ──
    if position == 'DEF':
        points += (stats.duels_won // 3) * SCORING_TABLE['duels_won_per_3']

    # ── FWD: Shots on target ──
    if position == 'FWD':
        points += (stats.shots_on_target // 2) * SCORING_TABLE['shots_on_target_per_2']

    return points


def _parse_accuracy(accuracy_str: str) -> float:
    """Parse pass accuracy string like '85%' or '85' to float."""
    if not accuracy_str:
        return 0.0
    try:
        return float(accuracy_str.replace('%', '').strip())
    except (ValueError, TypeError):
        return 0.0


def process_fixture_points(fixture):
    """
    Process all player stats for a fixture and update fantasy points.

    After calling this:
    - Each PlayerMatchStats gets its fantasy_points calculated
    - Each Player's total_fantasy_points and market_value are updated
    - Each User's total_points are updated based on their squad

    Args:
        fixture: Fixture instance (must be 'finished')
    """
    from .models import PlayerMatchStats, Player
    from squad.models import SquadPlayer
    from accounts.models import UserProfile
    from django.conf import settings
    from django.db.models import Q

    config = settings.GAME_CONFIG
    bench_multiplier = Decimal(str(config['BENCH_POINTS_MULTIPLIER']))

    # Step 1: Calculate fantasy points for every player in this fixture
    stats_list = PlayerMatchStats.objects.filter(fixture=fixture).select_related('player')
    for stats in stats_list:
        stats.fantasy_points = calculate_fantasy_points(stats)
        stats.save(update_fields=['fantasy_points'])

        # Update player's total fantasy points
        player = stats.player
        player.total_fantasy_points += stats.fantasy_points
        player.save(update_fields=['total_fantasy_points'])
        player.update_market_value()

    # Step 2: Award points to users based on their squads
    # Get all countries that played in this fixture
    playing_countries = [fixture.home_team_id, fixture.away_team_id]

    # Find all squad players whose player's country played in this fixture
    squad_players = SquadPlayer.objects.filter(
        player__country_id__in=playing_countries,
        player__match_stats__fixture=fixture
    ).select_related('player', 'squad', 'squad__user', 'squad__user__profile')

    # Track which users need auto-sub checks
    user_points = {}

    for sp in squad_players:
        user = sp.squad.user
        player_stats = PlayerMatchStats.objects.get(player=sp.player, fixture=fixture)
        earned = player_stats.fantasy_points

        if sp.is_starter:
            # Starter: full points
            multiplier = Decimal('1')
        else:
            # Bench: check if auto-sub should trigger
            # Auto-sub: if a starter of the same position's country isn't playing
            starter_same_pos = SquadPlayer.objects.filter(
                squad=sp.squad,
                is_starter=True,
                player__position=sp.player.position,
                player__country_id__in=playing_countries
            ).exists()

            if not starter_same_pos:
                # Auto-sub kicks in: full points
                multiplier = Decimal('1')
            else:
                # Normal bench: 50% points
                multiplier = bench_multiplier

        final_points = earned * multiplier

        if user.id not in user_points:
            user_points[user.id] = Decimal('0')
        user_points[user.id] += final_points

    # Step 3: Update user profiles
    for user_id, points in user_points.items():
        profile = UserProfile.objects.get(user_id=user_id)
        profile.total_points += points
        profile.save(update_fields=['total_points'])

    # Mark fixture as processed
    fixture.stats_processed = True
    fixture.save(update_fields=['stats_processed'])
