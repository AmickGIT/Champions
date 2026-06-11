from django.db import models
from django.contrib.auth.models import User

class Transaction(models.Model):
    TYPE_CHOICES = [
        ('starting_budget', 'Starting Budget'),
        ('bet_stake', 'Bet Stake'),
        ('bet_win', 'Bet Win'),
        ('bet_loss', 'Bet Loss'),
        ('transfer_buy', 'Transfer Buy'),
        ('transfer_sell', 'Transfer Sell'),
        ('compensation', 'Elimination Compensation'),
        ('auction_bid', 'Auction Bid'),
        ('auction_refund', 'Auction Refund'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    amount = models.DecimalField(max_digits=15, decimal_places=2, help_text='Positive = credit, Negative = debit')
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.amount}"

class SilentAuction(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
        ('cancelled', 'Cancelled'),
    ]
    country = models.ForeignKey('core.Country', on_delete=models.CASCADE, related_name='auctions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Auction for {self.country.name} - {self.status}"

class AuctionBid(models.Model):
    auction = models.ForeignKey(SilentAuction, on_delete=models.CASCADE, related_name='bids')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auction_bids')
    target_player = models.ForeignKey('core.Player', on_delete=models.CASCADE, related_name='auction_bids')
    bid_amount = models.DecimalField(max_digits=15, decimal_places=2)
    placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['auction', 'user', 'target_player']

    def __str__(self):
        return f"{self.user.username} bids {self.bid_amount} for {self.target_player.name}"
