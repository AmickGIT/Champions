from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

from .models import Transaction, SilentAuction, AuctionBid
from core.models import Player, Country
from squad.serializers import SquadPlayerSerializer
from .serializers import (
    TransactionSerializer, BuyPlayerSerializer, SellPlayerSerializer,
    SilentAuctionSerializer, PlaceAuctionBidSerializer, AuctionBidSerializer
)
from .services import TransferService


class BuyPlayerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BuyPlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        player = get_object_or_404(Player, id=serializer.validated_data['player_id'])
        drop_player = None
        if serializer.validated_data.get('drop_player_id'):
            drop_player = get_object_or_404(Player, id=serializer.validated_data['drop_player_id'])
            
        sp, error = TransferService.buy_player(request.user, player, drop_player)
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(SquadPlayerSerializer(sp).data, status=status.HTTP_201_CREATED)


class SellPlayerView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SellPlayerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        player = get_object_or_404(Player, id=serializer.validated_data['player_id'])
        
        success, message = TransferService.sell_player(request.user, player)
        
        if not success:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message': message})


class TransactionHistoryView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class ActiveAuctionsView(generics.ListAPIView):
    serializer_class = SilentAuctionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SilentAuction.objects.filter(status='open')


class PlaceAuctionBidView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, auction_id):
        auction = get_object_or_404(SilentAuction, id=auction_id)
        
        serializer = PlaceAuctionBidSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        target_player = get_object_or_404(Player, id=serializer.validated_data['target_player_id'])
        
        bid, error = TransferService.place_auction_bid(
            user=request.user,
            auction=auction,
            target_player=target_player,
            bid_amount=serializer.validated_data['bid_amount']
        )
        
        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(AuctionBidSerializer(bid).data, status=status.HTTP_201_CREATED)


class TriggerEliminationView(APIView):
    """Admin: Trigger elimination for a country."""
    permission_classes = [IsAdminUser]

    def post(self, request, country_id):
        country = get_object_or_404(Country, id=country_id)
        auction = TransferService.trigger_elimination_auction(country)
        return Response(SilentAuctionSerializer(auction).data, status=status.HTTP_201_CREATED)


class ResolveAuctionView(APIView):
    """Admin: Resolve an auction."""
    permission_classes = [IsAdminUser]

    def post(self, request, auction_id):
        auction = get_object_or_404(SilentAuction, id=auction_id)
        success, message = TransferService.resolve_auction(auction)
        
        if not success:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response({'message': message})
