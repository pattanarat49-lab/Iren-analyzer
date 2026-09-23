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

export type Horizon = "5m" | "15m" | "1h" | "eod";

export type Factor = { feature: string; label: string; value: string; impact: number; share: number };

export type HorizonPrediction =
  | { horizon: Horizon; label: string; available: false; reason: string }
  | {
      horizon: Horizon;
      label: string;
      available: true;
      p_up: number;
      p_down: number;
      model: "logreg" | "lgbm";
      calibration: string;
      edge: boolean;
      edge_reason: string;
      metrics: {
        accuracy: number;
        brier: number;
        auc: number | null;
        baseline_accuracy: number;
        baseline_brier: number;
        brier_diff_ci: [number, number];
        n_test: number;
        n_test_days: number;
        up_rate: number;
        reliability: { bin_low: number; bin_high: number; mean_p: number; observed: number; n: number }[];
      };
      factors: { up: Factor[]; down: Factor[] };
      expected_move: { minutes: number; move: number; move_pct: number; low: number; high: number } | null;
      trained_at: string;
      source: "alpaca" | "demo";
    };

export type Prediction = {
  as_of: DualTime;
  available: boolean;
  bar_time?: DualTime;
  price?: number;
  live_price?: number | null;
  horizons: Partial<Record<Horizon, HorizonPrediction>>;
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
  | { type: "analysis"; analysis: Analysis }
  | { type: "prediction"; prediction: Prediction };

export type CalibrationBin = { bin_low: number; bin_high: number; mean_p: number; observed: number; n: number };

export type TrackHorizon = {
  horizon: Horizon;
  label: string;
  n: number;
  pending: number;
  hit_rate?: number;
  baseline_hit_rate?: number;
  brier?: number;
  baseline_brier?: number;
  up_rate?: number;
  n_days?: number;
  brier_diff?: number;
  brier_diff_ci?: [number, number];
  verdict?: "insufficient" | "better" | "worse" | "no_difference";
  avg_p_up?: number;
  confident_n?: number;
  confident_hit_rate?: number | null;
  calibration?: CalibrationBin[];
  daily?: { day: string; n: number; hit_rate: number }[];
  recent?: { made_at: DualTime; p_up: number; price: number; outcome_price: number; outcome: number; hit: boolean }[];
};

export type RetrainStatus = {
  enabled: boolean;
  state: "idle" | "running" | "ok" | "failed";
  last_started: DualTime | null;
  last_finished: DualTime | null;
  last_message: string;
  next_run: DualTime | null;
};

export type TrackRecord = {
  as_of: DualTime;
  source: "alpaca" | "demo";
  days: number;
  horizons: Record<Horizon, TrackHorizon>;
  retrain: RetrainStatus;
};
