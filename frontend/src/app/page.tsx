"use client";

import Link from "next/link";
import { Trophy } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      router.push("/dashboard");
    } else {
      setIsLoading(false);
    }
  }, [router]);

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  }

  return (
    <div className="min-h-[calc(100vh-4rem)] flex flex-col items-center justify-center p-8 text-center">
      <div className="max-w-3xl space-y-8">
        <div className="flex justify-center mb-8">
          <Trophy className="h-24 w-24 text-primary" />
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
          Champions
        </h1>
        
        <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto">
          The ultimate private fantasy and betting platform for the FIFA World Cup 2026.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-8">
          <Link 
            href="/signup" 
            className="px-8 py-4 bg-primary text-primary-foreground font-semibold rounded-lg text-lg hover:bg-primary/90 transition-colors"
          >
            Create an Account
          </Link>
          <Link 
            href="/login" 
            className="px-8 py-4 bg-card border border-border text-card-foreground font-semibold rounded-lg text-lg hover:bg-card-hover transition-colors"
          >
            Log In
          </Link>
        </div>
      </div>
    </div>
  );
}
