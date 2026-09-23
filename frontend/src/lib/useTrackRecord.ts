"use client";

import { useEffect, useState } from "react";
import { backendUrl } from "./config";
import type { TrackRecord } from "./types";

/** Track record, refreshed every minute (outcomes are filled in on the backend every 30 s). */
export function useTrackRecord(days: number): { data: TrackRecord | null; error: boolean } {
  const [data, setData] = useState<TrackRecord | null>(null);
  const [error, setError] = useState(false);
  useEffect(() => {
    let stopped = false;
    const load = async () => {
      try {
        const r = await fetch(`${backendUrl()}/api/track-record?days=${days}`, { cache: "no-store" });
        if (!r.ok) throw new Error(String(r.status));
        const j = (await r.json()) as TrackRecord;
        if (!stopped) {
          setData(j);
          setError(false);
        }
      } catch {
        if (!stopped) setError(true);
      }
    };
    void load();
    const t = setInterval(load, 60_000);
    return () => {
      stopped = true;
      clearInterval(t);
    };
  }, [days]);
  return { data, error };
}
