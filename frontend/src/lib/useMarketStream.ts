"use client";

import { useEffect, useReducer, useRef } from "react";
import { backendUrl, wsUrl } from "./config";
import type { Analysis, Bar, DualTime, HubStatus, MarketState, Quote, ServerEvent } from "./types";

export type Link = "connecting" | "open" | "polling" | "offline";

export type StreamState = {
  link: Link;
  serverTime: DualTime | null;
  market: MarketState | null;
  status: HubStatus | null;
  quotes: Record<string, Quote>;
  analysis: Analysis | null;
  /** Increments whenever a completed/corrected bar arrives, keyed by symbol. */
  barSeq: Record<string, number>;
  lastBar: Record<string, Bar>;
  lastMessageAt: number | null;
};

const initial: StreamState = {
  link: "connecting",
  serverTime: null,
  market: null,
  status: null,
  quotes: {},
  analysis: null,
  barSeq: {},
  lastBar: {},
  lastMessageAt: null,
};

type Action =
  | { kind: "event"; event: ServerEvent }
  | { kind: "link"; link: Link }
  | { kind: "polled"; snapshot?: Extract<ServerEvent, { type: "snapshot" }>; analysis?: Analysis };

function reducer(s: StreamState, a: Action): StreamState {
  if (a.kind === "link") return s.link === a.link ? s : { ...s, link: a.link };
  if (a.kind === "polled") {
    let next = { ...s, lastMessageAt: Date.now() };
    if (a.snapshot) {
      next = {
        ...next,
        serverTime: a.snapshot.server_time,
        market: a.snapshot.market,
        status: a.snapshot.status,
        quotes: a.snapshot.quotes,
      };
    }
    if (a.analysis) next.analysis = a.analysis;
    return next;
  }
  const e = a.event;
  const base = { ...s, lastMessageAt: Date.now() };
  switch (e.type) {
    case "snapshot":
      return { ...base, serverTime: e.server_time, market: e.market, status: e.status, quotes: e.quotes };
    case "quote":
      return { ...base, quotes: { ...s.quotes, [e.quote.symbol]: e.quote } };
    case "bar":
      return {
        ...base,
        barSeq: { ...s.barSeq, [e.bar.symbol]: (s.barSeq[e.bar.symbol] ?? 0) + 1 },
        lastBar: { ...s.lastBar, [e.bar.symbol]: e.bar },
      };
    case "status":
      return { ...base, status: e.status };
    case "clock":
      return { ...base, serverTime: e.server_time, market: e.market };
    case "analysis":
      return { ...base, analysis: e.analysis };
    default:
      return base;
  }
}

const POLL_MS = 10_000;
const SILENCE_MS = 45_000; // backend sends a clock event every 15 s

/**
 * Live connection to the backend: WebSocket with exponential-backoff reconnect, a silence
 * watchdog, and REST polling while the socket is down.
 */
export function useMarketStream(): StreamState {
  const [state, dispatch] = useReducer(reducer, initial);
  const lastMsg = useRef<number>(0);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let stopped = false;
    let attempt = 0;
    let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
    let pollTimer: ReturnType<typeof setInterval> | undefined;

    const poll = async () => {
      try {
        const [snap, analysis] = await Promise.all([
          fetch(`${backendUrl()}/api/status`, { cache: "no-store" }).then((r) => (r.ok ? r.json() : undefined)),
          fetch(`${backendUrl()}/api/analysis`, { cache: "no-store" }).then((r) => (r.ok ? r.json() : undefined)),
        ]);
        if (!stopped) {
          dispatch({ kind: "polled", snapshot: snap, analysis });
          dispatch({ kind: "link", link: "polling" });
        }
      } catch {
        if (!stopped) dispatch({ kind: "link", link: "offline" });
      }
    };

    const startPolling = () => {
      if (pollTimer) return;
      void poll();
      pollTimer = setInterval(poll, POLL_MS);
    };
    const stopPolling = () => {
      if (pollTimer) clearInterval(pollTimer);
      pollTimer = undefined;
    };

    const connect = () => {
      if (stopped) return;
      dispatch({ kind: "link", link: "connecting" });
      try {
        ws = new WebSocket(wsUrl());
      } catch {
        scheduleReconnect();
        return;
      }
      ws.onopen = () => {
        attempt = 0;
        lastMsg.current = Date.now();
        stopPolling();
        dispatch({ kind: "link", link: "open" });
      };
      ws.onmessage = (m) => {
        lastMsg.current = Date.now();
        try {
          dispatch({ kind: "event", event: JSON.parse(m.data as string) as ServerEvent });
        } catch {
          /* ignore malformed frame */
        }
      };
      ws.onclose = () => {
        ws = null;
        if (!stopped) {
          startPolling();
          scheduleReconnect();
        }
      };
      ws.onerror = () => ws?.close();
    };

    const scheduleReconnect = () => {
      if (stopped) return;
      const delay = Math.min(30_000, 1000 * 2 ** attempt) + Math.random() * 500;
      attempt += 1;
      reconnectTimer = setTimeout(connect, delay);
    };

    const watchdog = setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN && Date.now() - lastMsg.current > SILENCE_MS) ws.close();
    }, 5_000);

    connect();
    return () => {
      stopped = true;
      clearTimeout(reconnectTimer);
      clearInterval(watchdog);
      stopPolling();
      ws?.close();
    };
  }, []);

  return state;
}
