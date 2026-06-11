"""
Draft service: snake draft logic, pick validation, squad creation.
"""
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction

from .models import Draft, DraftPick
from core.models import Player
from squad.models import Squad, SquadPlayer
from squad.services import assign_squad_positions


class DraftService:
    """Handles all draft business logic."""

    @staticmethod
    def generate_snake_order(user_ids, rounds=16):
        """
        Generate a snake-style draft order.

        For users [1, 2, 3, 4] with 16 rounds:
        Round 1: 1, 2, 3, 4
        Round 2: 4, 3, 2, 1
        Round 3: 1, 2, 3, 4
        ...

        Returns flat list of user IDs.
        """
        order = []
        for r in range(rounds):
            if r % 2 == 0:
                order.extend(user_ids)
            else:
                order.extend(reversed(user_ids))
        return order

    @staticmethod
    @transaction.atomic
    def start_draft(admin_user, participant_ids):
        """
        Create and start a new draft.

        Args:
            admin_user: The admin starting the draft
            participant_ids: List of user IDs participating

        Returns:
            Draft instance
        """
        # Validate participants exist
        participants = User.objects.filter(id__in=participant_ids)
        if participants.count() != len(participant_ids):
            raise ValueError("Some participant IDs are invalid")

        config = settings.GAME_CONFIG
        rounds = config['SQUAD_SIZE']  # 16 picks per player
        time_per_pick = config['DRAFT_TIME_PER_PICK_SECONDS']

        # Generate snake order
        order = DraftService.generate_snake_order(participant_ids, rounds)

        draft = Draft.objects.create(
            status='active',
            pick_order=order,
            current_pick_index=0,
            time_per_pick_seconds=time_per_pick,
            current_pick_deadline=timezone.now() + timedelta(seconds=time_per_pick),
            started_at=timezone.now(),
        )

        return draft

    @staticmethod
    @transaction.atomic
    def make_pick(draft, user, player):
        """
        Make a draft pick.

        Validates:
        - Draft is active
        - It's the user's turn
        - Player is available
        - User doesn't already have a player from this country

        Returns:
            (DraftPick, error_message)
        """
        if draft.status != 'active':
            return None, "Draft is not active"

        if draft.current_user_id != user.id:
            return None, "It's not your turn to pick"

        # Check if player is available
        if player.owner is not None:
            return None, f"{player.name} has already been picked"

        # Check country constraint: user can only have 1 player per country
        existing_countries = DraftPick.objects.filter(
            draft=draft,
            user=user
        ).values_list('player__country_id', flat=True)

        if player.country_id in list(existing_countries):
            return None, f"You already have a player from {player.country.name}"

        # Make the pick
        pick = DraftPick.objects.create(
            draft=draft,
            user=user,
            player=player,
            pick_number=draft.current_pick_index + 1,
        )

        # Mark player as owned
        player.owner = user
        player.is_available = False
        player.save(update_fields=['owner', 'is_available'])

        # Advance to next pick
        draft.current_pick_index += 1

        if draft.current_pick_index >= draft.total_picks:
            # Draft is complete
            draft.status = 'completed'
            draft.completed_at = timezone.now()
            draft.current_pick_deadline = None
            draft.save()

            # Create squads for all participants
            DraftService._create_squads_from_draft(draft)
        else:
            # Reset timer for next pick
            draft.current_pick_deadline = timezone.now() + timedelta(
                seconds=draft.time_per_pick_seconds
            )
            draft.save()

        return pick, None

    @staticmethod
    def _create_squads_from_draft(draft):
        """Create Squad objects for all participants after draft completion."""
        # Get unique participants
        participant_ids = set(draft.pick_order)
        config = settings.GAME_CONFIG

        for user_id in participant_ids:
            user = User.objects.get(id=user_id)

            # Get all players this user drafted
            picked_players = Player.objects.filter(
                draft_picks__draft=draft,
                draft_picks__user=user
            )

            # Create or get squad
            squad, _ = Squad.objects.get_or_create(
                user=user,
                defaults={'formation': config['DEFAULT_FORMATION']}
            )

            # Assign positions
            assign_squad_positions(squad, list(picked_players), config['DEFAULT_FORMATION'])

    @staticmethod
    def get_draft_state(draft):
        """
        Get the full state of the draft for the frontend.
        This is polled every 2-3 seconds.
        """
        picks = DraftPick.objects.filter(draft=draft).select_related(
            'user', 'player', 'player__country'
        ).order_by('pick_number')

        # Current user info
        current_user = None
        if draft.current_user_id:
            try:
                u = User.objects.get(id=draft.current_user_id)
                current_user = {'id': u.id, 'username': u.username}
            except User.DoesNotExist:
                pass

        # Time remaining
        time_remaining = None
        if draft.current_pick_deadline:
            delta = draft.current_pick_deadline - timezone.now()
            time_remaining = max(0, int(delta.total_seconds()))

        # Build pick order with usernames
        user_map = {}
        for uid in set(draft.pick_order):
            try:
                user_map[uid] = User.objects.get(id=uid).username
            except User.DoesNotExist:
                user_map[uid] = f"User {uid}"

        pick_order_named = [
            {'user_id': uid, 'username': user_map.get(uid, f'User {uid}')}
            for uid in draft.pick_order
        ]

        # Picks made so far
        picks_data = []
        for pick in picks:
            picks_data.append({
                'pick_number': pick.pick_number,
                'user_id': pick.user.id,
                'username': pick.user.username,
                'player': {
                    'id': pick.player.id,
                    'name': pick.player.name,
                    'position': pick.player.position,
                    'country': pick.player.country.name,
                    'country_code': pick.player.country.code,
                    'country_flag': pick.player.country.flag_url,
                    'photo_url': pick.player.photo_url,
                },
                'picked_at': pick.picked_at.isoformat(),
            })

        # Countries already picked by each user
        user_countries = {}
        for uid in set(draft.pick_order):
            user_picks = DraftPick.objects.filter(
                draft=draft, user_id=uid
            ).values_list('player__country_id', flat=True)
            user_countries[uid] = list(user_picks)

        return {
            'draft_id': draft.id,
            'status': draft.status,
            'current_pick_index': draft.current_pick_index,
            'total_picks': draft.total_picks,
            'current_user': current_user,
            'time_remaining': time_remaining,
            'time_per_pick': draft.time_per_pick_seconds,
            'pick_order': pick_order_named,
            'picks': picks_data,
            'picks_remaining': draft.picks_remaining,
            'user_countries': user_countries,
            'started_at': draft.started_at.isoformat() if draft.started_at else None,
            'completed_at': draft.completed_at.isoformat() if draft.completed_at else None,
        }

    @staticmethod
    @transaction.atomic
    def auto_pick(draft):
        """
        Auto-pick for the current user (when timer expires).
        Picks the available player with the highest market value,
        respecting country constraints.
        """
        if draft.status != 'active':
            return None, "Draft is not active"

        user_id = draft.current_user_id
        if not user_id:
            return None, "No current user"

        user = User.objects.get(id=user_id)

        # Get countries already picked by this user
        picked_countries = DraftPick.objects.filter(
            draft=draft, user=user
        ).values_list('player__country_id', flat=True)

        # Find best available player not from a picked country
        available = Player.objects.filter(
            owner__isnull=True
        ).exclude(
            country_id__in=list(picked_countries)
        ).order_by('-market_value', 'name')

        if not available.exists():
            return None, "No available players"

        player = available.first()
        return DraftService.make_pick(draft, user, player)
