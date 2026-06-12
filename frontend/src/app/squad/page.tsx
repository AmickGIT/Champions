"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Users, Settings, ArrowLeftRight } from "lucide-react";

export default function SquadPage() {
  const [squad, setSquad] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchSquad = async () => {
    try {
      const res = await api.get("squad/");
      setSquad(res.data);
    } catch (err: any) {
      if (err.response?.status === 404) {
        setError("You don't have a squad yet. Complete the draft first.");
      } else {
        setError("Failed to load squad. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSquad();
  }, []);

  if (loading) return <div className="p-8">Loading squad...</div>;
  if (error) return <div className="p-8 text-muted-foreground">{error}</div>;
  if (!squad) return null;

  const starters = squad.players.filter((p: any) => p.is_starter);
  const bench = squad.players.filter((p: any) => !p.is_starter);

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="text-primary w-8 h-8" />
            My Squad
          </h1>
          <p className="text-muted-foreground mt-2">
            Formation: <span className="font-semibold text-foreground">{squad.formation}</span>
          </p>
        </div>
        <div className="bg-card px-6 py-3 rounded-xl border border-border">
          <p className="text-sm text-muted-foreground">Total Points</p>
          <p className="text-2xl font-bold text-primary">{squad.total_points}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Starters */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-xl font-semibold">Starting XI</h2>
          <div className="bg-card border border-border rounded-xl p-4">
            <div className="space-y-2">
              {starters.map((sp: any) => (
                <div key={sp.id} className="flex items-center justify-between p-3 rounded-lg border border-border hover:border-primary/50 transition-colors bg-background">
                  <div className="flex items-center gap-4">
                    <div className="w-10 text-center font-bold text-muted-foreground bg-secondary py-1 rounded">
                      {sp.position_slot.replace(/\d+$/, '')}
                    </div>
                    {sp.player.photo_url ? (
                      <img src={sp.player.photo_url} alt="" className="w-10 h-10 rounded-full object-cover" />
                    ) : (
                      <div className="w-10 h-10 rounded-full bg-secondary"></div>
                    )}
                    <div>
                      <div className="font-bold">{sp.player.name}</div>
                      <div className="text-xs flex items-center gap-2 text-muted-foreground">
                        {sp.player.country_flag && <img src={sp.player.country_flag} alt="" className="w-4 h-4 rounded-sm object-cover" />}
                        {sp.player.country_name}
                      </div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-primary">{sp.player.total_fantasy_points} pts</div>
                    <div className="text-xs text-muted-foreground">${(sp.player.market_value / 1000000).toFixed(1)}M</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bench */}
        <div className="lg:col-span-1 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            Substitutes
          </h2>
          <div className="bg-card border border-border rounded-xl p-4">
            <div className="space-y-2">
              {bench.map((sp: any) => (
                <div key={sp.id} className="flex flex-col p-3 rounded-lg border border-border bg-background">
                  <div className="flex items-center justify-between mb-2">
                    <div className="text-xs font-bold text-muted-foreground bg-secondary px-2 py-0.5 rounded">
                      {sp.position_slot}
                    </div>
                    <div className="text-xs font-bold text-primary">{sp.player.total_fantasy_points} pts</div>
                  </div>
                  <div className="flex items-center gap-3">
                    {sp.player.photo_url ? (
                      <img src={sp.player.photo_url} alt="" className="w-8 h-8 rounded-full object-cover" />
                    ) : (
                      <div className="w-8 h-8 rounded-full bg-secondary"></div>
                    )}
                    <div>
                      <div className="font-semibold text-sm">{sp.player.name}</div>
                      <div className="text-xs text-muted-foreground">{sp.player.country_code} • {sp.player.position}</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 pt-4 border-t border-border">
              <p className="text-sm text-muted-foreground text-center">
                Bench players earn 50% points. <br/>Auto-subs trigger if a starter's team doesn't play.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
