from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from .models import BettingOdds, Bet
from core.models import Fixture
# Note: we need to delay import of Transaction to avoid circular dependencies if it hasn't been created yet.
# We'll import it inside the methods.

class BettingService:
    @staticmethod
    def get_odds_for_fixture(fixture):
        """Format odds for frontend consumption."""
        odds_records = BettingOdds.objects.filter(fixture=fixture)
        result = {}
        for record in odds_records:
            result[record.bet_type] = record.odds_data
        return result

    @staticmethod
    @transaction.atomic
    def place_bet(user, fixture, bet_type, prediction, stake):
        from transfers.models import Transaction

        # Validation
        if fixture.kick_off <= timezone.now():
            return None, "Cannot place bet on a fixture that has already started"

        if bet_type not in ['match_winner', 'exact_score']:
            return None, "Invalid bet type"

        try:
            odds_record = BettingOdds.objects.get(fixture=fixture, bet_type=bet_type)
        except BettingOdds.DoesNotExist:
            return None, "Odds not available for this fixture and bet type"

        # Find the specific odds value for the prediction
        selected_odd = None
        for option in odds_record.odds_data:
            if str(option['value']) == str(prediction):
                selected_odd = Decimal(str(option['odd']))
                break
                
        if not selected_odd:
            return None, f"Prediction '{prediction}' not found in available odds"

        # Check balance
        profile = user.profile
        if profile.balance < stake:
            return None, "Insufficient balance"

        # Place bet
        profile.balance -= stake
        profile.save(update_fields=['balance'])

        bet = Bet.objects.create(
            user=user,
            fixture=fixture,
            bet_type=bet_type,
            prediction=prediction,
            odds=selected_odd,
            stake=stake,
            status='pending'
        )

        Transaction.objects.create(
            user=user,
            type='bet_stake',
            amount=-stake,
            description=f"Placed bet on {fixture}: {bet_type} - {prediction}"
        )

        return bet, None

    @staticmethod
    @transaction.atomic
    def resolve_bets_for_fixture(fixture):
        from transfers.models import Transaction

        if fixture.status != 'finished':
            return False, "Fixture is not finished yet"
            
        pending_bets = Bet.objects.filter(fixture=fixture, status='pending')
        
        for bet in pending_bets:
            won = False
            if bet.bet_type == 'match_winner':
                won = (bet.prediction == fixture.result)
            elif bet.bet_type == 'exact_score':
                won = (bet.prediction == fixture.score_string)
                
            if won:
                bet.status = 'won'
                bet.payout = bet.stake * bet.odds
                
                # Update balance
                profile = bet.user.profile
                profile.balance += bet.payout
                profile.save(update_fields=['balance'])
                
                # Transaction
                Transaction.objects.create(
                    user=bet.user,
                    type='bet_win',
                    amount=bet.payout,
                    description=f"Won bet on {fixture}: {bet.bet_type} - {bet.prediction}"
                )
            else:
                bet.status = 'lost'
                bet.payout = 0
                
                Transaction.objects.create(
                    user=bet.user,
                    type='bet_loss',
                    amount=0,
                    description=f"Lost bet on {fixture}: {bet.bet_type} - {bet.prediction}"
                )
                
            bet.resolved_at = timezone.now()
            bet.save()
            
        return True, f"Resolved {pending_bets.count()} bets"
