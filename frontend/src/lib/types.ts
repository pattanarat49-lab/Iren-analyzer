// Shapes of the FastAPI backend payloads (see backend/app/main.py).

export type DualTime = { utc: string; et: string; bkk: string };

export type Session = "pre" | "regular" | "after" | "closed";

export type MarketState = {
  session: Session;
  label_th: string;
  is_half_day: boolean;
  next_regular_open: DualTime;
  next_regular_close: DualTime;
};

export type ConnectionMode = "starting" | "live" | "polling" | "demo" | "error";

export type HubStatus = {
  mode: ConnectionMode;
  detail: string;
  streams: Record<string, string>;
  source: "alpaca" | "demo";
  stock_feed: string;
  primary_symbol: string;
  stock_symbols: string[];
  crypto_symbols: string[];
};

export type Bar = {
  symbol: string;
  ts: string;
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type Quote = {
  symbol: string;
  price: number | null;
  prev_close: number | null;
  change: number | null;
  change_pct: number | null;
  after_hours_change: number | null;
  after_hours_change_pct: number | null;
  bid: number | null;
  ask: number | null;
  halted: boolean;
  halt_reason: string;
  updated: DualTime | null;
  forming_bar: Bar | null;
};

export type Signal = "bullish" | "bearish" | "neutral";

export type IndicatorSignal = {
  key: string;
  name: string;
  value: number | null;
  display: string;
  signal: Signal;
  explanation: string;
  extra: Record<string, unknown> | null;
};

export type RelativeRow = {
  symbol: string;
  price: number | null;
  change_today: number | null;
  change_1h: number | null;
  corr_60: number | null;
  corr_390: number | null;
  beta_390: number | null;
  rs_today: number | null;
  rs_1h: number | null;
  signal: Signal;
  explanation: string;
};

export type Analysis =
  | { ready: false; symbol: string; tf: number; as_of: DualTime; message: string }
  | {
      ready: true;
      symbol: string;
      tf: number;
      as_of: DualTime;
      bar_time: DualTime;
      price: number;
      bars_used: number;
      iex_only: boolean;
      indicators: IndicatorSignal[];
      summary: { overall: Signal; counts: Record<Signal, number>; explanation: string };
      values: Record<string, number | null>;
      relative: RelativeRow[];
    };

export type ChartPoint = { time: number; value: number };
export type ChartPayload = {
  symbol: string;
  tf: number;
  bars: { time: number; open: number; high: number; low: number; close: number; volume: number }[];
  series: Record<string, ChartPoint[]>;
};

export type ServerEvent =
  | {
      type: "snapshot";
      server_time: DualTime;
      market: MarketState;
      status: HubStatus;
      quotes: Record<string, Quote>;
    }
  | { type: "quote"; quote: Quote }
  | { type: "bar"; updated: boolean; bar: Bar }
  | { type: "status"; status: HubStatus }
  | { type: "clock"; server_time: DualTime; market: MarketState }
  | { type: "analysis"; analysis: Analysis };
