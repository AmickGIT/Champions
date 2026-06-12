from django.urls import path
from . import views

urlpatterns = [
    path('transfers/buy/', views.BuyPlayerView.as_view(), name='buy-player'),
    path('transfers/sell/', views.SellPlayerView.as_view(), name='sell-player'),
    path('transactions/', views.TransactionHistoryView.as_view(), name='transactions'),
    path('auctions/', views.ActiveAuctionsView.as_view(), name='active-auctions'),
    path('auctions/<int:auction_id>/bid/', views.PlaceAuctionBidView.as_view(), name='place-bid'),
    
    # Admin endpoints
    path('auctions/trigger/<int:country_id>/', views.TriggerEliminationView.as_view(), name='trigger-auction'),
    path('auctions/resolve/<int:auction_id>/', views.ResolveAuctionView.as_view(), name='resolve-auction'),
]
