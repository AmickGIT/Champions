"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { DollarSign, Clock, CheckCircle } from "lucide-react";
import { format } from "date-fns";

export default function BettingPage() {
  const [fixtures, setFixtures] = useState([]);
  const [myBets, setMyBets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [balance, setBalance] = useState(0);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [fixturesRes, betsRes, profileRes] = await Promise.all([
          api.get("fixtures/upcoming/"),
          api.get("betting/my-bets/"),
          api.get("auth/profile/")
        ]);
        setFixtures(fixturesRes.data);
        setMyBets(betsRes.data);
        setBalance(profileRes.data.balance);
      } catch (err) {
        console.error("Failed to load betting data");
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  const [selectedFixture, setSelectedFixture] = useState<any>(null);
  const [odds, setOdds] = useState<any>(null);
  const [prediction, setPrediction] = useState("");
  const [stake, setStake] = useState("");
  const [betLoading, setBetLoading] = useState(false);

  const fetchOdds = async (fixture: any) => {
    setSelectedFixture(fixture);
    setOdds(null);
    setPrediction("");
    try {
      const res = await api.get(`betting/odds/${fixture.id}/`);
      setOdds(res.data.odds);
    } catch (err) {
      console.error("Failed to load odds");
    }
  };

  const handlePlaceBet = async () => {
    if (!prediction || !stake) return;
    setBetLoading(true);
    try {
      await api.post("betting/place/", {
        fixture_id: selectedFixture.id,
        bet_type: "match_winner", // Assuming match winner for simplicity
        prediction: prediction,
        stake: stake
      });
      alert("Bet placed successfully!");
      // Reload bets and balance
      const [betsRes, profileRes] = await Promise.all([
        api.get("betting/my-bets/"),
        api.get("auth/profile/")
      ]);
      setMyBets(betsRes.data);
      setBalance(profileRes.data.balance);
      setSelectedFixture(null);
    } catch (err: any) {
      alert(err.response?.data?.error || "Failed to place bet");
    } finally {
      setBetLoading(false);
      setStake("");
    }
  };

  if (loading) return <div className="p-8">Loading betting markets...</div>;

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <DollarSign className="text-primary w-8 h-8" />
            Sportsbook
          </h1>
          <p className="text-muted-foreground mt-2">Place bets on upcoming World Cup matches</p>
        </div>
        <div className="bg-card px-6 py-3 rounded-xl border border-border">
          <p className="text-sm text-muted-foreground">Available Balance</p>
          <p className="text-2xl font-bold text-accent">${parseFloat(balance.toString()).toLocaleString()}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Match List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Upcoming Matches</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {fixtures.map((match: any) => (
              <div 
                key={match.id} 
                onClick={() => fetchOdds(match)}
                className={`bg-card border rounded-xl p-4 cursor-pointer transition-all ${selectedFixture?.id === match.id ? 'border-primary ring-1 ring-primary' : 'border-border hover:border-primary/50'}`}
              >
                <div className="text-xs text-muted-foreground mb-3 text-center">
                  {format(new Date(match.kick_off), "MMM d, yyyy • h:mm a")}
                </div>
                <div className="flex items-center justify-between">
                  <div className="font-semibold">{match.home_team.name}</div>
                  <div className="text-muted-foreground text-sm font-bold">VS</div>
                  <div className="font-semibold">{match.away_team.name}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Bet Slip */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold">Bet Slip</h2>
          
          <div className="bg-card border border-border rounded-xl p-5 sticky top-24">
            {!selectedFixture ? (
              <div className="text-center text-muted-foreground py-8">
                Select a match to view odds and place a bet.
              </div>
            ) : (
              <div className="space-y-6">
                <div className="text-center border-b border-border pb-4">
                  <div className="font-bold mb-1">Match Winner</div>
                  <div className="text-sm text-muted-foreground">
                    {selectedFixture.home_team.name} vs {selectedFixture.away_team.name}
                  </div>
                </div>

                {!odds ? (
                  <div className="text-center py-4">Loading odds...</div>
                ) : !odds.match_winner ? (
                  <div className="text-center text-destructive py-4">Odds not available yet for this match.</div>
                ) : (
                  <div className="space-y-4">
                    <div className="grid grid-cols-3 gap-2">
                      {odds.match_winner.map((opt: any) => (
                        <button
                          key={opt.value}
                          onClick={() => setPrediction(opt.value)}
                          className={`p-2 rounded border text-sm flex flex-col items-center ${prediction === opt.value ? 'bg-primary text-primary-foreground border-primary' : 'bg-background border-border hover:border-primary/50'}`}
                        >
                          <span className="font-semibold">{opt.value === 'Home' ? '1' : opt.value === 'Away' ? '2' : 'X'}</span>
                          <span>{opt.odd}</span>
                        </button>
                      ))}
                    </div>

                    <div className="pt-4 space-y-2">
                      <label className="text-sm font-medium text-muted-foreground">Stake Amount ($)</label>
                      <input 
                        type="number" 
                        value={stake}
                        onChange={(e) => setStake(e.target.value)}
                        placeholder="e.g. 500000"
                        className="w-full p-3 bg-input border border-border rounded focus:outline-none focus:border-primary"
                      />
                    </div>

                    {prediction && stake && odds.match_winner.find((o:any)=>o.value===prediction) && (
                      <div className="bg-background rounded p-3 text-sm flex justify-between border border-border">
                        <span className="text-muted-foreground">Potential Payout:</span>
                        <span className="font-bold text-accent">
                          ${(parseFloat(stake) * parseFloat(odds.match_winner.find((o:any)=>o.value===prediction).odd)).toLocaleString(undefined, {maximumFractionDigits: 0})}
                        </span>
                      </div>
                    )}

                    <button 
                      onClick={handlePlaceBet}
                      disabled={!prediction || !stake || betLoading}
                      className="w-full py-3 bg-primary text-primary-foreground font-semibold rounded disabled:opacity-50 hover:bg-primary/90 transition-colors"
                    >
                      {betLoading ? "Processing..." : "Place Bet"}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* My Bets */}
      <div className="pt-8 space-y-4">
        <h2 className="text-xl font-semibold">My Active Bets</h2>
        <div className="bg-card border border-border rounded-xl overflow-hidden">
          {myBets.length > 0 ? (
            <table className="w-full text-sm text-left">
              <thead className="bg-secondary text-secondary-foreground uppercase font-semibold">
                <tr>
                  <th className="px-4 py-3">Match</th>
                  <th className="px-4 py-3">Prediction</th>
                  <th className="px-4 py-3 text-right">Odds</th>
                  <th className="px-4 py-3 text-right">Stake</th>
                  <th className="px-4 py-3 text-right">Status</th>
                </tr>
              </thead>
              <tbody>
                {myBets.map((bet: any) => (
                  <tr key={bet.id} className="border-b border-border last:border-0 hover:bg-card-hover">
                    <td className="px-4 py-3 font-medium">
                      {bet.fixture.home_team.name} vs {bet.fixture.away_team.name}
                    </td>
                    <td className="px-4 py-3">{bet.prediction}</td>
                    <td className="px-4 py-3 text-right">{bet.odds}</td>
                    <td className="px-4 py-3 text-right">${parseFloat(bet.stake).toLocaleString()}</td>
                    <td className="px-4 py-3 text-right">
                      {bet.status === 'pending' ? (
                        <span className="flex items-center justify-end gap-1 text-muted-foreground"><Clock className="w-4 h-4"/> Pending</span>
                      ) : bet.status === 'won' ? (
                        <span className="flex items-center justify-end gap-1 text-accent"><CheckCircle className="w-4 h-4"/> Won</span>
                      ) : (
                        <span className="text-destructive">Lost</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-muted-foreground">
              You haven't placed any bets yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
