from datetime import timedelta
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from django.db.models import Max
from .models import Transaction, SilentAuction, AuctionBid
from core.models import Player, Country
from squad.models import SquadPlayer, Squad

class TransferService:
    @staticmethod
    def get_player_value(player):
        """Calculate market value."""
        config = settings.GAME_CONFIG
        base = Decimal(str(config['PLAYER_BASE_VALUE']))
        multiplier = Decimal(str(config['POINTS_VALUE_MULTIPLIER']))
        return base + (Decimal(str(player.total_fantasy_points)) * multiplier)

    @staticmethod
    @transaction.atomic
    def buy_player(user, player, drop_player=None):
        if player.owner is not None:
            return None, f"{player.name} is already owned by another user"
            
        if not player.is_available:
            return None, f"{player.name} is currently not available"

        # Check country constraint
        existing_countries = set(
            p.player.country_id for p in SquadPlayer.objects.filter(squad__user=user)
        )
        
        if drop_player:
            if drop_player.country_id in existing_countries:
                existing_countries.remove(drop_player.country_id)
                
        if player.country_id in existing_countries:
            return None, f"You already have a player from {player.country.name}"

        # Squad size logic
        squad = Squad.objects.get(user=user)
        squad_size = squad.players.count()
        config = settings.GAME_CONFIG
        max_size = config['SQUAD_SIZE']

        if squad_size >= max_size and not drop_player:
            return None, f"Your squad is full ({max_size} players). You must drop a player."
            
        if drop_player:
            try:
                squad_player = SquadPlayer.objects.get(squad=squad, player=drop_player)
            except SquadPlayer.DoesNotExist:
                return None, "The player you want to drop is not in your squad"
                
            if drop_player.position != player.position:
                return None, f"You must drop a {player.position} to buy a {player.position}"

        # Check balance
        market_value = TransferService.get_player_value(player)
        profile = user.profile
        
        if profile.balance < market_value:
            return None, f"Insufficient balance. {player.name} costs {market_value}"

        # Process Drop
        if drop_player:
            squad_player.delete()
            drop_player.owner = None
            drop_player.is_available = True
            drop_player.save(update_fields=['owner', 'is_available'])
            
            # Since drop happens as part of buy, we don't give the sell credit.
            # Sell credit is only for selling a player explicitly. Wait, maybe we should give sell credit?
            # User wants: Buy/Sell or Swap. Let's make explicit Sell and Buy separate or handled together here.
            pass

        # Process Buy
        profile.balance -= market_value
        profile.save(update_fields=['balance'])
        
        player.owner = user
        player.is_available = False
        player.market_value = market_value
        player.save(update_fields=['owner', 'is_available', 'market_value'])
        
        position_slot = squad_player.position_slot if drop_player else f"SUB_{player.position}"
        is_starter = squad_player.is_starter if drop_player else False

        new_sp = SquadPlayer.objects.create(
            squad=squad,
            player=player,
            is_starter=is_starter,
            position_slot=position_slot
        )

        Transaction.objects.create(
            user=user,
            type='transfer_buy',
            amount=-market_value,
            description=f"Bought {player.name} for {market_value}"
        )
        
        return new_sp, None

    @staticmethod
    @transaction.atomic
    def sell_player(user, player):
        try:
            squad = Squad.objects.get(user=user)
            sp = SquadPlayer.objects.get(squad=squad, player=player)
        except (Squad.DoesNotExist, SquadPlayer.DoesNotExist):
            return False, "Player is not in your squad"

        config = settings.GAME_CONFIG
        market_value = TransferService.get_player_value(player)
        sell_value = market_value * Decimal(str(config['SELL_PENALTY_RATE']))

        sp.delete()
        player.owner = None
        player.is_available = True
        player.save(update_fields=['owner', 'is_available'])

        profile = user.profile
        profile.balance += sell_value
        profile.save(update_fields=['balance'])

        Transaction.objects.create(
            user=user,
            type='transfer_sell',
            amount=sell_value,
            description=f"Sold {player.name} for {sell_value}"
        )

        return True, "Player sold successfully"

    @staticmethod
    @transaction.atomic
    def trigger_elimination_auction(country):
        country.is_eliminated = True
        country.save(update_fields=['is_eliminated'])

        config = settings.GAME_CONFIG
        compensation_rate = Decimal(str(config['ELIMINATION_COMPENSATION_RATE']))
        auction_hours = config['AUCTION_DURATION_HOURS']

        affected_squad_players = SquadPlayer.objects.filter(
            player__country=country
        ).select_related('squad__user', 'player')

        for sp in affected_squad_players:
            user = sp.squad.user
            player = sp.player
            
            market_value = TransferService.get_player_value(player)
            compensation = market_value * compensation_rate
            
            sp.delete()
            player.owner = None
            player.is_available = True
            player.save(update_fields=['owner', 'is_available'])
            
            profile = user.profile
            profile.balance += compensation
            profile.save(update_fields=['balance'])
            
            Transaction.objects.create(
                user=user,
                type='compensation',
                amount=compensation,
                description=f"Compensation for eliminated player {player.name}"
            )

        opens_at = timezone.now()
        closes_at = opens_at + timedelta(hours=auction_hours)
        
        auction = SilentAuction.objects.create(
            country=country,
            status='open',
            opens_at=opens_at,
            closes_at=closes_at
        )
        
        return auction

    @staticmethod
    @transaction.atomic
    def place_auction_bid(user, auction, target_player, bid_amount):
        if auction.status != 'open' or timezone.now() > auction.closes_at:
            return None, "Auction is closed"
            
        if target_player.owner is not None or not target_player.is_available:
            return None, "Player is not available"
            
        existing_countries = SquadPlayer.objects.filter(
            squad__user=user
        ).values_list('player__country_id', flat=True)
        
        if target_player.country_id in list(existing_countries):
            return None, f"You already have a player from {target_player.country.name}"

        # Check existing bid to refund or update
        existing_bid = AuctionBid.objects.filter(auction=auction, user=user, target_player=target_player).first()
        
        profile = user.profile
        additional_needed = bid_amount
        if existing_bid:
            additional_needed = bid_amount - existing_bid.bid_amount
            
        if profile.balance < additional_needed:
            return None, "Insufficient balance for this bid"

        profile.balance -= additional_needed
        profile.save(update_fields=['balance'])

        if existing_bid:
            existing_bid.bid_amount = bid_amount
            existing_bid.save()
            bid = existing_bid
        else:
            bid = AuctionBid.objects.create(
                auction=auction,
                user=user,
                target_player=target_player,
                bid_amount=bid_amount
            )
            
        Transaction.objects.create(
            user=user,
            type='auction_bid',
            amount=-additional_needed,
            description=f"Bid on {target_player.name}"
        )
        
        return bid, None

    @staticmethod
    @transaction.atomic
    def resolve_auction(auction):
        if auction.status != 'open':
            return False, "Auction already resolved or cancelled"
            
        bids = AuctionBid.objects.filter(auction=auction)
        
        # Group bids by target player
        player_bids = {}
        for bid in bids:
            if bid.target_player_id not in player_bids:
                player_bids[bid.target_player_id] = []
            player_bids[bid.target_player_id].append(bid)
            
        for player_id, p_bids in player_bids.items():
            # Find max bid
            max_bid_amount = max(b.bid_amount for b in p_bids)
            top_bids = [b for b in p_bids if b.bid_amount == max_bid_amount]
            
            winner_bid = top_bids[0]
            if len(top_bids) > 1:
                # Tie breaker: fewest total points
                winner_bid = min(top_bids, key=lambda b: b.user.profile.total_points)
                
            for bid in p_bids:
                if bid == winner_bid:
                    player = bid.target_player
                    user = bid.user
                    
                    player.owner = user
                    player.is_available = False
                    player.market_value = bid.bid_amount
                    player.save(update_fields=['owner', 'is_available', 'market_value'])
                    
                    squad, _ = Squad.objects.get_or_create(user=user)
                    SquadPlayer.objects.create(
                        squad=squad,
                        player=player,
                        is_starter=False,
                        position_slot=f"SUB_{player.position}"
                    )
                else:
                    # Refund losers
                    profile = bid.user.profile
                    profile.balance += bid.bid_amount
                    profile.save(update_fields=['balance'])
                    
                    Transaction.objects.create(
                        user=bid.user,
                        type='auction_refund',
                        amount=bid.bid_amount,
                        description=f"Refund for lost bid on {bid.target_player.name}"
                    )

        auction.status = 'resolved'
        auction.save()
        return True, "Auction resolved"
