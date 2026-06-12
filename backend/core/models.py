from django.db import models
from django.contrib.auth.models import User


class Country(models.Model):
    """Represents a nation participating in the World Cup."""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, unique=True, help_text="ISO country code, e.g. BR, AR")
    flag_url = models.URLField(blank=True)
    api_team_id = models.IntegerField(unique=True, help_text="API-Football team ID")
    is_eliminated = models.BooleanField(default=False)
    group = models.CharField(max_length=10, blank=True, help_text="e.g. Group A")

    class Meta:
        verbose_name_plural = 'Countries'
        ordering = ['name']

    def __str__(self):
        return self.name


class Player(models.Model):
    """Represents a football player in the World Cup."""
    POSITION_CHOICES = [
        ('GK', 'Goalkeeper'),
        ('DEF', 'Defender'),
        ('MID', 'Midfielder'),
        ('FWD', 'Forward'),
    ]

    name = models.CharField(max_length=200)
    photo_url = models.URLField(blank=True)
    api_player_id = models.IntegerField(unique=True, help_text="API-Football player ID")
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='players')
    position = models.CharField(max_length=3, choices=POSITION_CHOICES)
    market_value = models.DecimalField(max_digits=15, decimal_places=2, default=5000000)
    total_fantasy_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    owner = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='owned_players',
        help_text="Current owner (exclusive ownership)"
    )
    is_available = models.BooleanField(default=True, help_text="Available for draft/transfer")
    jersey_number = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ['country', 'position', 'name']

    def __str__(self):
        return f"{self.name} ({self.country.code} - {self.position})"

    def update_market_value(self):
        """Recalculate market value based on fantasy points."""
        from django.conf import settings
        config = settings.GAME_CONFIG
        base = config['PLAYER_BASE_VALUE']
        multiplier = config['POINTS_VALUE_MULTIPLIER']
        self.market_value = base + (float(self.total_fantasy_points) * multiplier)
        self.save(update_fields=['market_value'])


class Fixture(models.Model):
    """Represents a World Cup match."""
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),
        ('finished', 'Finished'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]

    api_fixture_id = models.IntegerField(unique=True, help_text="API-Football fixture ID")
    home_team = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='home_fixtures')
    away_team = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='away_fixtures')
    kick_off = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    home_score = models.IntegerField(null=True, blank=True)
    away_score = models.IntegerField(null=True, blank=True)
    round = models.CharField(max_length=100, blank=True, help_text="e.g. Group A - 1, Round of 16")
    venue = models.CharField(max_length=200, blank=True)
    stats_processed = models.BooleanField(default=False, help_text="Whether fantasy points have been calculated")

    class Meta:
        ordering = ['kick_off']

    def __str__(self):
        return f"{self.home_team} vs {self.away_team} ({self.kick_off.strftime('%Y-%m-%d')})"

    @property
    def result(self):
        """Returns 'Home', 'Draw', or 'Away' based on scores."""
        if self.home_score is None or self.away_score is None:
            return None
        if self.home_score > self.away_score:
            return 'Home'
        elif self.home_score < self.away_score:
            return 'Away'
        return 'Draw'

    @property
    def score_string(self):
        """Returns score as 'H:A' format for exact score betting."""
        if self.home_score is None or self.away_score is None:
            return None
        return f"{self.home_score}:{self.away_score}"


class PlayerMatchStats(models.Model):
    """Stores player statistics from a specific match, fetched from API-Football."""
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='match_stats')
    fixture = models.ForeignKey(Fixture, on_delete=models.CASCADE, related_name='player_stats')

    # Game info
    minutes_played = models.IntegerField(default=0)
    position_played = models.CharField(max_length=3, blank=True, help_text="Position in this match: G/D/M/F")
    rating = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    was_substitute = models.BooleanField(default=False)

    # Goals & Assists
    goals = models.IntegerField(default=0)
    assists = models.IntegerField(default=0)
    goals_conceded = models.IntegerField(default=0)

    # Saves (GK)
    saves = models.IntegerField(default=0)

    # Passes
    passes_total = models.IntegerField(default=0)
    passes_key = models.IntegerField(default=0)
    pass_accuracy = models.CharField(max_length=10, blank=True, help_text="e.g. '85%'")

    # Tackles & Defense
    tackles = models.IntegerField(default=0)
    interceptions = models.IntegerField(default=0)
    blocks = models.IntegerField(default=0)

    # Duels
    duels_total = models.IntegerField(default=0)
    duels_won = models.IntegerField(default=0)

    # Dribbles
    dribbles_attempted = models.IntegerField(default=0)
    dribbles_success = models.IntegerField(default=0)

    # Shots
    shots_total = models.IntegerField(default=0)
    shots_on_target = models.IntegerField(default=0)

    # Fouls
    fouls_drawn = models.IntegerField(default=0)
    fouls_committed = models.IntegerField(default=0)

    # Cards
    yellow_cards = models.IntegerField(default=0)
    red_cards = models.IntegerField(default=0)

    # Penalties
    penalties_scored = models.IntegerField(default=0)
    penalties_missed = models.IntegerField(default=0)
    penalties_saved = models.IntegerField(default=0)
    penalties_won = models.IntegerField(default=0)

    # Calculated
    fantasy_points = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        unique_together = ['player', 'fixture']
        verbose_name_plural = 'Player match stats'

    def __str__(self):
        return f"{self.player.name} in {self.fixture} - {self.fantasy_points} pts"
