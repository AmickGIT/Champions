from django.db import models
from django.contrib.auth.models import User


class Draft(models.Model):
    """Represents a snake-style draft session."""
    STATUS_CHOICES = [
        ('waiting', 'Waiting for Players'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    pick_order = models.JSONField(
        default=list,
        help_text='Flat snake-order array of user IDs for all rounds'
    )
    current_pick_index = models.IntegerField(default=0)
    time_per_pick_seconds = models.IntegerField(default=60)
    current_pick_deadline = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Draft #{self.id} - {self.status}"

    @property
    def total_picks(self):
        return len(self.pick_order)

    @property
    def current_user_id(self):
        if self.current_pick_index < len(self.pick_order):
            return self.pick_order[self.current_pick_index]
        return None

    @property
    def picks_remaining(self):
        return max(0, self.total_picks - self.current_pick_index)


class DraftPick(models.Model):
    """A single pick made during the draft."""
    draft = models.ForeignKey(Draft, on_delete=models.CASCADE, related_name='picks')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='draft_picks')
    player = models.ForeignKey('core.Player', on_delete=models.CASCADE, related_name='draft_picks')
    pick_number = models.IntegerField()
    picked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['pick_number']
        unique_together = ['draft', 'pick_number']

    def __str__(self):
        return f"Pick #{self.pick_number}: {self.user.username} → {self.player.name}"
