from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Squad(models.Model):
    """A user's fantasy squad."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='squad')
    formation = models.CharField(
        max_length=10,
        default='4-3-3',
        help_text='e.g. 4-3-3, 3-5-2'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Squad ({self.formation})"

    @property
    def starters(self):
        return self.players.filter(is_starter=True)

    @property
    def bench(self):
        return self.players.filter(is_starter=False)

    @property
    def total_points(self):
        """Sum of all players' fantasy points (weighted by starter/bench)."""
        from decimal import Decimal
        total = Decimal('0')
        bench_mult = Decimal(str(settings.GAME_CONFIG['BENCH_POINTS_MULTIPLIER']))
        for sp in self.players.select_related('player').all():
            if sp.is_starter:
                total += sp.player.total_fantasy_points
            else:
                total += sp.player.total_fantasy_points * bench_mult
        return total


class SquadPlayer(models.Model):
    """A player slot in a user's squad."""
    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, related_name='players')
    player = models.ForeignKey('core.Player', on_delete=models.CASCADE, related_name='squad_positions')
    is_starter = models.BooleanField(default=True)
    position_slot = models.CharField(
        max_length=10,
        help_text='Position slot: GK, DEF1, DEF2, MID1, FWD1, SUB_GK, SUB1, etc.'
    )

    class Meta:
        unique_together = ['squad', 'player']
        ordering = ['is_starter', 'position_slot']

    def __str__(self):
        status = "Starting" if self.is_starter else "Bench"
        return f"{self.player.name} ({self.position_slot}) - {status}"
