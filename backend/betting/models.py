from django.db import models
from django.contrib.auth.models import User

class BettingOdds(models.Model):
    fixture = models.ForeignKey('core.Fixture', on_delete=models.CASCADE, related_name='betting_odds')
    bet_type = models.CharField(max_length=50, help_text='match_winner or exact_score')
    odds_data = models.JSONField(help_text='Full odds object from API-Football')
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Betting odds'
        unique_together = ['fixture', 'bet_type']

    def __str__(self):
        return f"Odds for {self.fixture} - {self.bet_type}"

class Bet(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('won', 'Won'),
        ('lost', 'Lost'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets')
    fixture = models.ForeignKey('core.Fixture', on_delete=models.CASCADE, related_name='bets')
    bet_type = models.CharField(max_length=50)  # match_winner or exact_score
    prediction = models.CharField(max_length=50)  # 'Home', 'Draw', 'Away' or '2:1'
    odds = models.DecimalField(max_digits=8, decimal_places=2)
    stake = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payout = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    placed_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.fixture} - {self.prediction} @ {self.odds}"
