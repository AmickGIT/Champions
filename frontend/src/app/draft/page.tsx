"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Users, Clock, CheckCircle } from "lucide-react";

export default function DraftRoom() {
  const [draftState, setDraftState] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [availablePlayers, setAvailablePlayers] = useState([]);
  const [isPolling, setIsPolling] = useState(true);

  // Poll draft state
  useEffect(() => {
    let interval: NodeJS.Timeout;

    const fetchDraftState = async () => {
      try {
        const res = await api.get("draft/state/");
        setDraftState(res.data);
        
        // If draft is completed, stop polling
        if (res.data.status === "completed") {
          setIsPolling(false);
        }
        
      } catch (err: any) {
        if (err.response?.status === 404) {
          setError("No active draft found. Wait for admin to start one.");
          setIsPolling(false);
        }
      } finally {
        setLoading(false);
      }
    };

    if (isPolling) {
      fetchDraftState();
      interval = setInterval(fetchDraftState, 3000); // Poll every 3 seconds
    }

    return () => clearInterval(interval);
  }, [isPolling]);

  // Fetch players once
  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const res = await api.get("players/?available=true");
        setAvailablePlayers(res.data);
      } catch (err) {
        console.error("Failed to load players");
      }
    };
    fetchPlayers();
  }, []);

  const handlePick = async (playerId: number) => {
    try {
      await api.post("draft/pick/", { player_id: playerId });
      // Remove from available list instantly for better UX
      setAvailablePlayers(prev => prev.filter((p: any) => p.id !== playerId));
    } catch (err: any) {
      alert(err.response?.data?.error || "Failed to make pick");
    }
  };

  if (loading) return <div className="p-8">Loading draft room...</div>;
  if (error) return <div className="p-8 text-destructive">{error}</div>;
  if (!draftState) return null;

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="text-primary w-8 h-8" />
            Live Draft Room
          </h1>
          <p className="text-muted-foreground mt-2">
            Status: <span className="uppercase font-semibold text-foreground">{draftState.status}</span>
          </p>
        </div>
        
        {draftState.status === "active" && draftState.current_user && (
          <div className="bg-card border border-primary/50 rounded-xl p-4 flex items-center gap-4 shadow-lg">
            <div>
              <p className="text-sm text-muted-foreground">Current Pick</p>
              <p className="font-bold text-lg text-primary">{draftState.current_user.username}</p>
            </div>
            <div className="h-10 w-px bg-border"></div>
            <div className="flex items-center gap-2 text-destructive font-mono text-xl font-bold">
              <Clock className="w-5 h-5" />
              {draftState.time_remaining !== null ? `${draftState.time_remaining}s` : "--"}
            </div>
          </div>
        )}
      </div>

      {draftState.status === "completed" && (
        <div className="bg-accent/20 border border-accent text-accent rounded-xl p-6 flex flex-col items-center justify-center text-center">
          <CheckCircle className="w-12 h-12 mb-4" />
          <h2 className="text-2xl font-bold mb-2">Draft Complete!</h2>
          <p>All squads have been finalized. Head over to the Squad page to view your team.</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Available Players Pool */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Available Players</h2>
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            <div className="max-h-[600px] overflow-y-auto">
              <table className="w-full text-sm text-left">
                <thead className="bg-secondary text-secondary-foreground uppercase font-semibold sticky top-0">
                  <tr>
                    <th className="px-4 py-3">Player</th>
                    <th className="px-4 py-3">Position</th>
                    <th className="px-4 py-3">Country</th>
                    <th className="px-4 py-3 text-right">Value</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody>
                  {availablePlayers.map((player: any) => (
                    <tr key={player.id} className="border-b border-border last:border-0 hover:bg-card-hover">
                      <td className="px-4 py-3 font-medium flex items-center gap-3">
                        {player.photo_url ? (
                          <img src={player.photo_url} alt={player.name} className="w-8 h-8 rounded-full object-cover" />
                        ) : (
                          <div className="w-8 h-8 rounded-full bg-secondary"></div>
                        )}
                        {player.name}
                      </td>
                      <td className="px-4 py-3">{player.position}</td>
                      <td className="px-4 py-3 flex items-center gap-2">
                        {player.country_flag && <img src={player.country_flag} alt="" className="w-5 h-5 rounded-sm object-cover" />}
                        {player.country_name}
                      </td>
                      <td className="px-4 py-3 text-right">${(player.market_value / 1000000).toFixed(1)}M</td>
                      <td className="px-4 py-3 text-right">
                        <button 
                          onClick={() => handlePick(player.id)}
                          disabled={draftState.status !== "active" || draftState.current_user?.id !== player.id} // we'll need real logic to check if current logged in user is picking
                          className="px-3 py-1.5 bg-primary text-primary-foreground rounded text-xs font-semibold hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                          Draft
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Draft History / Order */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold">Pick History</h2>
          <div className="bg-card border border-border rounded-xl p-4 max-h-[600px] overflow-y-auto space-y-3">
            {draftState.picks?.length > 0 ? (
              draftState.picks.map((pick: any) => (
                <div key={pick.pick_number} className="flex gap-3 p-3 rounded-lg border border-border bg-secondary/50">
                  <div className="font-mono text-muted-foreground font-bold w-8 shrink-0">#{pick.pick_number}</div>
                  <div className="flex-1">
                    <div className="text-xs text-muted-foreground mb-1">{pick.username} drafted:</div>
                    <div className="font-semibold flex items-center gap-2">
                      {pick.player.photo_url && <img src={pick.player.photo_url} alt="" className="w-5 h-5 rounded-full" />}
                      {pick.player.name} ({pick.player.position})
                    </div>
                  </div>
                </div>
              )).reverse() // Show newest at top
            ) : (
              <div className="text-center text-muted-foreground p-4">No picks made yet.</div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
