"use client";

import { useState, useEffect } from "react";
import api from "@/lib/api";
import { Trophy, Calendar } from "lucide-react";
import { format } from "date-fns";

export default function Dashboard() {
  const [leaderboard, setLeaderboard] = useState([]);
  const [upcomingMatches, setUpcomingMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        // We will fetch real data from endpoints once built
        const [lbRes, fixturesRes] = await Promise.all([
          api.get("leaderboard/").catch(() => ({ data: [] })),
          api.get("fixtures/upcoming/").catch(() => ({ data: [] }))
        ]);
        
        setLeaderboard(lbRes.data);
        setUpcomingMatches(fixturesRes.data);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return <div className="p-8">Loading dashboard...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8 space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Leaderboard Section */}
        <div className="lg:col-span-1 space-y-4">
          <div className="flex items-center gap-2">
            <Trophy className="text-primary w-5 h-5" />
            <h2 className="text-xl font-semibold">Leaderboard</h2>
          </div>
          
          <div className="bg-card border border-border rounded-xl overflow-hidden">
            {leaderboard.length > 0 ? (
              <table className="w-full text-sm text-left">
                <thead className="bg-secondary text-secondary-foreground uppercase font-semibold">
                  <tr>
                    <th className="px-4 py-3">Rank</th>
                    <th className="px-4 py-3">Manager</th>
                    <th className="px-4 py-3 text-right">Points</th>
                  </tr>
                </thead>
                <tbody>
                  {leaderboard.map((user: any, idx) => (
                    <tr key={user.id} className="border-b border-border last:border-0 hover:bg-card-hover">
                      <td className="px-4 py-3 font-medium">{idx + 1}</td>
                      <td className="px-4 py-3">{user.user.username}</td>
                      <td className="px-4 py-3 text-right font-bold text-primary">{user.total_points}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                No ranking data available yet.
              </div>
            )}
          </div>
        </div>

        {/* Upcoming Matches Section */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center gap-2">
            <Calendar className="text-primary w-5 h-5" />
            <h2 className="text-xl font-semibold">Upcoming Fixtures</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {upcomingMatches.length > 0 ? (
              upcomingMatches.map((match: any) => (
                <div key={match.id} className="bg-card border border-border rounded-xl p-4 flex flex-col justify-between hover:border-primary/50 transition-colors">
                  <div className="text-xs text-muted-foreground mb-2 text-center">
                    {format(new Date(match.kick_off), "MMM d, yyyy • h:mm a")} | {match.round}
                  </div>
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex flex-col items-center flex-1">
                      {match.home_team.flag_url ? (
                        <img src={match.home_team.flag_url} alt={match.home_team.name} className="w-8 h-8 rounded-full mb-1 object-cover" />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-secondary mb-1"></div>
                      )}
                      <span className="font-semibold text-center">{match.home_team.name}</span>
                    </div>
                    <div className="px-4 font-bold text-muted-foreground">VS</div>
                    <div className="flex flex-col items-center flex-1">
                      {match.away_team.flag_url ? (
                        <img src={match.away_team.flag_url} alt={match.away_team.name} className="w-8 h-8 rounded-full mb-1 object-cover" />
                      ) : (
                        <div className="w-8 h-8 rounded-full bg-secondary mb-1"></div>
                      )}
                      <span className="font-semibold text-center">{match.away_team.name}</span>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-full p-8 bg-card border border-border rounded-xl text-center text-muted-foreground">
                No upcoming fixtures scheduled.
              </div>
            )}
          </div>
        </div>
        
      </div>
    </div>
  );
}
