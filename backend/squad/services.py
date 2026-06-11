"""
Squad management services: formation validation, auto-sub logic.
"""
from django.conf import settings
from .models import Squad, SquadPlayer


# Formation definitions: formation string -> {position: count}
FORMATION_MAP = {
    '4-3-3': {'DEF': 4, 'MID': 3, 'FWD': 3},
    '4-4-2': {'DEF': 4, 'MID': 4, 'FWD': 2},
    '3-5-2': {'DEF': 3, 'MID': 5, 'FWD': 2},
    '3-4-3': {'DEF': 3, 'MID': 4, 'FWD': 3},
    '4-2-3-1': {'DEF': 4, 'MID': 5, 'FWD': 1},
    '4-5-1': {'DEF': 4, 'MID': 5, 'FWD': 1},
    '5-3-2': {'DEF': 5, 'MID': 3, 'FWD': 2},
    '5-4-1': {'DEF': 5, 'MID': 4, 'FWD': 1},
}


def validate_formation(formation, squad):
    """
    Validate that a squad's starters match the given formation.
    Returns (is_valid, error_message).
    """
    if formation not in FORMATION_MAP:
        return False, f"Invalid formation: {formation}. Valid: {list(FORMATION_MAP.keys())}"

    required = FORMATION_MAP[formation]
    starters = squad.starters.select_related('player')

    # Must have exactly 1 GK
    gk_count = starters.filter(player__position='GK').count()
    if gk_count != 1:
        return False, f"Must have exactly 1 GK starter, found {gk_count}"

    # Check outfield positions
    for pos, count in required.items():
        actual = starters.filter(player__position=pos).count()
        if actual != count:
            return False, f"Formation {formation} requires {count} {pos}, found {actual}"

    # Total starters must be 11
    total = starters.count()
    if total != 11:
        return False, f"Must have exactly 11 starters, found {total}"

    return True, None


def generate_position_slots(formation):
    """Generate position slot names for a formation."""
    slots = ['GK']
    required = FORMATION_MAP.get(formation, FORMATION_MAP['4-3-3'])

    for pos, count in required.items():
        for i in range(1, count + 1):
            slots.append(f"{pos}{i}")

    return slots


def assign_squad_positions(squad, players, formation='4-3-3'):
    """
    Assign players to squad positions based on formation.
    Players should already be owned by the user.

    Args:
        squad: Squad instance
        players: list of Player instances (16 total)
        formation: formation string
    """
    config = settings.GAME_CONFIG
    required = FORMATION_MAP.get(formation, FORMATION_MAP['4-3-3'])

    # Sort players by position
    gks = [p for p in players if p.position == 'GK']
    defs = [p for p in players if p.position == 'DEF']
    mids = [p for p in players if p.position == 'MID']
    fwds = [p for p in players if p.position == 'FWD']

    starter_slots = []

    # Assign GK starter
    if gks:
        starter_slots.append((gks[0], 'GK', True))

    # Assign outfield starters based on formation
    def_needed = required.get('DEF', 4)
    mid_needed = required.get('MID', 3)
    fwd_needed = required.get('FWD', 3)

    for i, p in enumerate(defs[:def_needed]):
        starter_slots.append((p, f'DEF{i+1}', True))
    for i, p in enumerate(mids[:mid_needed]):
        starter_slots.append((p, f'MID{i+1}', True))
    for i, p in enumerate(fwds[:fwd_needed]):
        starter_slots.append((p, f'FWD{i+1}', True))

    # Assign bench
    assigned_ids = {p.id for p, _, _ in starter_slots}
    bench_players = [p for p in players if p.id not in assigned_ids]

    bench_slots = []
    sub_gk_assigned = False
    sub_counter = 1

    for p in bench_players:
        if p.position == 'GK' and not sub_gk_assigned:
            bench_slots.append((p, 'SUB_GK', False))
            sub_gk_assigned = True
        else:
            bench_slots.append((p, f'SUB{sub_counter}', False))
            sub_counter += 1

    # Create SquadPlayer records
    all_slots = starter_slots + bench_slots
    created = []
    for player, slot, is_starter in all_slots:
        sp, _ = SquadPlayer.objects.update_or_create(
            squad=squad,
            player=player,
            defaults={
                'is_starter': is_starter,
                'position_slot': slot,
            }
        )
        created.append(sp)

    squad.formation = formation
    squad.save(update_fields=['formation'])

    return created


def swap_players(squad, player1_id, player2_id):
    """
    Swap two players' starter/bench status in a squad.
    Returns (success, error_message).
    """
    try:
        sp1 = SquadPlayer.objects.get(squad=squad, player_id=player1_id)
        sp2 = SquadPlayer.objects.get(squad=squad, player_id=player2_id)
    except SquadPlayer.DoesNotExist:
        return False, "One or both players not found in your squad"

    # Swap is_starter and position_slot
    sp1.is_starter, sp2.is_starter = sp2.is_starter, sp1.is_starter
    sp1.position_slot, sp2.position_slot = sp2.position_slot, sp1.position_slot

    sp1.save(update_fields=['is_starter', 'position_slot'])
    sp2.save(update_fields=['is_starter', 'position_slot'])

    return True, None
