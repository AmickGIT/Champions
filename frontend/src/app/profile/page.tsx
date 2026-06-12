"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { User, Wallet, ArrowDownUp, ShieldAlert } from "lucide-react";
import { format } from "date-fns";

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [transactions, setTransactions] = useState([]);
  const [auctions, setAuctions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profRes, transRes, auctRes] = await Promise.all([
          api.get("auth/profile/"),
          api.get("transactions/"),
          api.get("auctions/")
        ]);
        setProfile(profRes.data);
        setTransactions(transRes.data);
        setAuctions(auctRes.data);
      } catch (err) {
        console.error("Failed to load profile data");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleBid = async (auctionId: number, playerId: number) => {
    const amount = prompt("Enter your bid amount in dollars:");
    if (!amount) return;

    try {
      await api.post(`auctions/${auctionId}/bid/`, {
        target_player_id: playerId,
        bid_amount: parseFloat(amount)
      });
      alert("Bid placed successfully!");
      // Reload profile to reflect balance
      const profRes = await api.get("auth/profile/");
      setProfile(profRes.data);
    } catch (err: any) {
      alert(err.response?.data?.error || "Failed to place bid");
    }
  };

  if (loading) return <div className="p-8">Loading profile...</div>;

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
      <div className="flex items-center gap-4">
        <div className="w-16 h-16 bg-primary/20 text-primary rounded-full flex items-center justify-center">
          <User className="w-8 h-8" />
        </div>
        <div>
          <h1 className="text-3xl font-bold">{profile.user.username}</h1>
          <p className="text-muted-foreground">{profile.user.email}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-card border border-border rounded-xl p-6 flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground flex items-center gap-2 mb-1">
              <Wallet className="w-4 h-4" /> Available Balance
            </p>
            <p className="text-4xl font-bold text-accent">${parseFloat(profile.balance).toLocaleString()}</p>
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-6 flex items-center justify-between">
          <div>
            <p className="text-sm text-muted-foreground mb-1">Total Fantasy Points</p>
            <p className="text-4xl font-bold text-primary">{profile.total_points}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Silent Auctions */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <ShieldAlert className="text-destructive w-5 h-5" /> 
            Active Auctions
          </h2>
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            {auctions.length > 0 ? (
              <div className="p-4 space-y-4">
                {auctions.map((auction: any) => (
                  <div key={auction.id} className="border border-destructive/50 bg-destructive/10 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="font-bold flex items-center gap-2">
                          {auction.country.flag_url && <img src={auction.country.flag_url} className="w-5 h-5 rounded-sm" />}
                          {auction.country.name} Eliminated
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">
                          Closes: {format(new Date(auction.closes_at), "MMM d, h:mm a")}
                        </div>
                      </div>
                      <div className="text-xs bg-destructive text-destructive-foreground px-2 py-1 rounded font-bold uppercase">
                        Auction Open
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      Bid on available players from {auction.country.name}. Highest sealed bid wins.
                    </p>
                    {/* Placeholder for player list - would normally fetch available players from this country */}
                    <button 
                      onClick={() => alert("Browse players feature coming soon to view.")}
                      className="text-sm bg-background border border-border px-3 py-1.5 rounded hover:border-primary transition-colors w-full"
                    >
                      Browse {auction.country.name} Players
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                No active auctions. Auctions trigger when a country is eliminated.
              </div>
            )}
          </div>
        </div>

        {/* Transaction History */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <ArrowDownUp className="w-5 h-5" />
            Transaction History
          </h2>
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <div className="max-h-[500px] overflow-y-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-secondary text-secondary-foreground sticky top-0">
                  <tr>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3">Type</th>
                    <th className="px-4 py-3 text-right">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map((tx: any) => (
                    <tr key={tx.id} className="border-b border-border last:border-0 hover:bg-card-hover">
                      <td className="px-4 py-3 text-muted-foreground">
                        {format(new Date(tx.created_at), "MMM d, h:mm a")}
                      </td>
                      <td className="px-4 py-3">
                        <div className="font-medium capitalize">{tx.type.replace('_', ' ')}</div>
                        <div className="text-xs text-muted-foreground">{tx.description}</div>
                      </td>
                      <td className={`px-4 py-3 text-right font-bold ${parseFloat(tx.amount) >= 0 ? 'text-accent' : 'text-destructive'}`}>
                        {parseFloat(tx.amount) > 0 ? '+' : ''}{parseFloat(tx.amount).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                  {transactions.length === 0 && (
                    <tr>
                      <td colSpan={3} className="px-4 py-8 text-center text-muted-foreground">
                        No transactions found.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
