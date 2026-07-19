"use client";

import { useAuth, useUser } from "@clerk/nextjs";
import { useEffect } from "react";

const SYNC_STORAGE_KEY = "clerk-neon-sync";

export function ClerkNeonSync() {
  const { isLoaded, isSignedIn } = useAuth();
  const { user } = useUser();

  useEffect(() => {
    if (!isLoaded || !isSignedIn || !user?.id) {
      return;
    }

    const key = `${SYNC_STORAGE_KEY}:${user.id}`;
    if (sessionStorage.getItem(key) === "done") {
      return;
    }

    let cancelled = false;

    const syncUser = async () => {
      try {
        const response = await fetch("/api/auth/sync", { method: "POST" });
        if (!cancelled && response.ok) {
          sessionStorage.setItem(key, "done");
        }
      } catch {
        // Retry on next navigation/render if the sync call fails.
      }
    };

    void syncUser();

    return () => {
      cancelled = true;
    };
  }, [isLoaded, isSignedIn, user?.id]);

  return null;
}
