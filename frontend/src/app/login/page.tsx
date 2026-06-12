"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import api from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await api.post("auth/token/", {
        username,
        password,
      });

      if (response.data.access) {
        localStorage.setItem("access_token", response.data.access);
        localStorage.setItem("refresh_token", response.data.refresh);
        router.push("/dashboard");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || 
        "Invalid credentials. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md p-8 bg-card rounded-xl border border-border shadow-xl">
        <h2 className="text-3xl font-bold mb-6 text-center">Welcome Back</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-destructive/20 border border-destructive/50 text-destructive-foreground rounded text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 text-muted-foreground">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 bg-input border border-border rounded focus:outline-none focus:border-primary"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-1 text-muted-foreground">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 bg-input border border-border rounded focus:outline-none focus:border-primary"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full p-3 mt-4 bg-primary text-primary-foreground font-semibold rounded hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>
        
        <p className="mt-6 text-center text-sm text-muted-foreground">
          Don't have an account?{" "}
          <Link href="/signup" className="text-primary hover:underline">
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
