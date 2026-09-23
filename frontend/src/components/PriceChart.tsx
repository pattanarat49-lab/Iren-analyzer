"use client";

import {
  CandlestickSeries,
  ColorType,
  CrosshairMode,
  HistogramSeries,
  LineSeries,
  LineStyle,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type LineData,
  type MouseEventParams,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";
import { backendUrl } from "@/lib/config";
import { dayMonth, fmtPrice, hhmm } from "@/lib/format";
import type { Bar, ChartPayload } from "@/lib/types";

const C = {
  surface: "#1a1a19",
  muted: "#898781",
  grid: "#2c2c2a",
  axis: "#383835",
  up: "#0ca30c",
  down: "#d03b3b",
  upVol: "rgba(12,163,12,0.35)",
  downVol: "rgba(208,59,59,0.35)",
  s1: "#3987e5",
  s2: "#d95926",
  s3: "#199e70",
  s4: "#c98500",
};

type OverlayKey = "ema9" | "ema21" | "ema50" | "vwap" | "bb";
const OVERLAYS: { key: OverlayKey; label: string; color: string; dashed?: boolean }[] = [
  { key: "ema9", label: "EMA 9", color: C.s1 },
  { key: "ema21", label: "EMA 21", color: C.s2 },
  { key: "ema50", label: "EMA 50", color: C.s3 },
  { key: "vwap", label: "VWAP", color: C.s4, dashed: true },
  { key: "bb", label: "Bollinger", color: C.muted, dashed: true },
];

type Series = {
  candles: ISeriesApi<"Candlestick">;
  volume: ISeriesApi<"Histogram">;
  lines: Record<string, ISeriesApi<"Line">>;
  macdHist: ISeriesApi<"Histogram">;
};

type Legend = { time: number; o: number; h: number; l: number; c: number; values: Record<string, number | undefined> } | null;

const ET = "America/New_York";
const BKK = "Asia/Bangkok";

function toLine(points: { time: number; value: number }[] = []): LineData[] {
  return points.map((p) => ({ time: p.time as UTCTimestamp, value: p.value }));
}

export function PriceChart({
  symbol,
  tf,
  refreshKey,
  forming,
}: {
  symbol: string;
  tf: number;
  /** Changes whenever a new bar is stored; triggers a reload of the chart data. */
  refreshKey: number;
  /** The live, not-yet-completed 1-minute candle for `symbol`. */
  forming: Bar | null | undefined;
}) {
  const box = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<Series | null>(null);
  const lastBars = useRef<ChartPayload["bars"]>([]);
  const [visible, setVisible] = useState<Record<OverlayKey, boolean>>({ ema9: true, ema21: true, ema50: true, vwap: true, bb: true });
  const [legend, setLegend] = useState<Legend>(null);
  const [latest, setLatest] = useState<Legend>(null);
  const [error, setError] = useState<string | null>(null);
  const [empty, setEmpty] = useState(false);
  const fitNext = useRef(true);

  // ---- create the chart once ----
  useEffect(() => {
    if (!box.current) return;
    const chart = createChart(box.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: C.surface },
        textColor: C.muted,
        fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif",
        panes: { separatorColor: C.axis, separatorHoverColor: C.grid },
      },
      grid: { vertLines: { color: C.grid }, horzLines: { color: C.grid } },
      rightPriceScale: { borderColor: C.axis },
      crosshair: { mode: CrosshairMode.Normal },
      timeScale: {
        borderColor: C.axis,
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 4,
        tickMarkFormatter: (t: Time, type: number) => {
          const sec = Number(t);
          // 0-2 = year/month/day marks -> show date; otherwise time in ET
          return type <= 2 ? dayMonth(sec, ET) : hhmm(sec, ET);
        },
      },
      localization: {
        timeFormatter: (t: Time) => {
          const sec = Number(t);
          return `${dayMonth(sec, ET)} ${hhmm(sec, ET)} ET · ${hhmm(sec, BKK)} ไทย`;
        },
        priceFormatter: (p: number) => fmtPrice(p),
      },
    });

    const candles = chart.addSeries(CandlestickSeries, {
      upColor: C.up,
      downColor: C.down,
      borderVisible: false,
      wickUpColor: C.up,
      wickDownColor: C.down,
      priceLineVisible: true,
    });
    const volume = chart.addSeries(HistogramSeries, {
      priceScaleId: "vol",
      priceFormat: { type: "volume" },
      lastValueVisible: false,
      priceLineVisible: false,
    });
    chart.priceScale("vol").applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });

    const line = (color: string, opts: Record<string, unknown> = {}, pane = 0) =>
      chart.addSeries(LineSeries, { color, lineWidth: 2, priceLineVisible: false, crosshairMarkerVisible: false, ...opts }, pane);

    const lines: Record<string, ISeriesApi<"Line">> = {
      ema9: line(C.s1, { title: "EMA9" }),
      ema21: line(C.s2, { title: "EMA21" }),
      ema50: line(C.s3, { title: "EMA50" }),
      vwap: line(C.s4, { title: "VWAP", lineStyle: LineStyle.Dashed }),
      bb_upper: line(C.muted, { lineWidth: 1, lineStyle: LineStyle.Dotted, lastValueVisible: false }),
      bb_mid: line(C.muted, { lineWidth: 1, lineStyle: LineStyle.Dotted, lastValueVisible: false }),
      bb_lower: line(C.muted, { lineWidth: 1, lineStyle: LineStyle.Dotted, lastValueVisible: false }),
      rsi14: line(C.s1, { title: "RSI" }, 1),
      macd: line(C.s1, { title: "MACD" }, 2),
      signal: line(C.s2, { title: "Signal" }, 2),
    };
    for (const lvl of [70, 30]) {
      lines.rsi14.createPriceLine({ price: lvl, color: C.muted, lineWidth: 1, lineStyle: LineStyle.Dashed, axisLabelVisible: true, title: "" });
    }
    const macdHist = chart.addSeries(HistogramSeries, { priceLineVisible: false, lastValueVisible: false }, 2);

    const panes = chart.panes();
    panes[0]?.setStretchFactor(3.2);
    panes[1]?.setStretchFactor(1);
    panes[2]?.setStretchFactor(1);

    const onMove = (param: MouseEventParams) => {
      if (!param.time) {
        setLegend(null);
        return;
      }
      const cd = param.seriesData.get(candles) as { open: number; high: number; low: number; close: number } | undefined;
      if (!cd) return;
      const values: Record<string, number | undefined> = {};
      for (const [k, s] of Object.entries(lines)) {
        const d = param.seriesData.get(s) as { value?: number } | undefined;
        values[k] = d?.value;
      }
      setLegend({ time: Number(param.time), o: cd.open, h: cd.high, l: cd.low, c: cd.close, values });
    };
    chart.subscribeCrosshairMove(onMove);

    // Axis-label titles ("EMA9", "VWAP"…) are direct labels on wide screens; on phones they would
    // cover the newest candles, so there the legend row above the chart carries the names.
    const TITLES: Record<string, string> = { ema9: "EMA9", ema21: "EMA21", ema50: "EMA50", vwap: "VWAP", rsi14: "RSI", macd: "MACD", signal: "Signal" };
    const applyTitles = () => {
      const wide = (box.current?.clientWidth ?? 0) >= 640;
      for (const [k, title] of Object.entries(TITLES)) lines[k].applyOptions({ title: wide ? title : "" });
    };
    applyTitles();
    const ro = new ResizeObserver(applyTitles);
    ro.observe(box.current);

    chartRef.current = chart;
    seriesRef.current = { candles, volume, lines, macdHist };
    return () => {
      ro.disconnect();
      chart.unsubscribeCrosshairMove(onMove);
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  // ---- (re)load data ----
  useEffect(() => {
    fitNext.current = true;
  }, [symbol, tf]);

  useEffect(() => {
    const ctrl = new AbortController();
    const load = async () => {
      try {
        const r = await fetch(`${backendUrl()}/api/chart?symbol=${encodeURIComponent(symbol)}&tf=${tf}&limit=600`, {
          cache: "no-store",
          signal: ctrl.signal,
        });
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        const p = (await r.json()) as ChartPayload;
        const s = seriesRef.current;
        if (!s) return;
        lastBars.current = p.bars;
        const b = p.bars[p.bars.length - 1];
        if (b) {
          const values: Record<string, number | undefined> = {};
          for (const [k, pts] of Object.entries(p.series)) values[k] = pts[pts.length - 1]?.value;
          setLatest({ time: b.time, o: b.open, h: b.high, l: b.low, c: b.close, values });
        } else {
          setLatest(null);
        }
        setEmpty(p.bars.length === 0);
        s.candles.setData(p.bars.map((b) => ({ time: b.time as UTCTimestamp, open: b.open, high: b.high, low: b.low, close: b.close })));
        s.volume.setData(
          p.bars.map((b) => ({ time: b.time as UTCTimestamp, value: b.volume, color: b.close >= b.open ? C.upVol : C.downVol })),
        );
        for (const [k, series] of Object.entries(s.lines)) series.setData(toLine(p.series[k]));
        s.macdHist.setData(
          (p.series.hist ?? []).map((pt) => ({ time: pt.time as UTCTimestamp, value: pt.value, color: pt.value >= 0 ? C.upVol : C.downVol })),
        );
        if (fitNext.current && p.bars.length) {
          chartRef.current?.timeScale().setVisibleLogicalRange({ from: Math.max(0, p.bars.length - 180), to: p.bars.length + 4 });
          fitNext.current = false;
        }
        setError(null);
      } catch (e) {
        if ((e as Error).name !== "AbortError") setError("โหลดกราฟไม่สำเร็จ จะลองใหม่เมื่อมีแท่งเทียนใหม่");
      }
    };
    void load();
    return () => ctrl.abort();
  }, [symbol, tf, refreshKey]);

  // ---- live forming candle ----
  useEffect(() => {
    const s = seriesRef.current;
    const bars = lastBars.current;
    if (!s || !forming || !bars.length) return;
    const bucket = Math.floor(forming.time / (tf * 60)) * tf * 60;
    const last = bars[bars.length - 1];
    if (bucket < last.time) return;
    const merged =
      bucket === last.time
        ? { ...last, high: Math.max(last.high, forming.high), low: Math.min(last.low, forming.low), close: forming.close }
        : { time: bucket, open: forming.open, high: forming.high, low: forming.low, close: forming.close, volume: forming.volume };
    s.candles.update({ time: merged.time as UTCTimestamp, open: merged.open, high: merged.high, low: merged.low, close: merged.close });
  }, [forming, tf]);

  // ---- overlay toggles ----
  useEffect(() => {
    const s = seriesRef.current;
    if (!s) return;
    s.lines.ema9.applyOptions({ visible: visible.ema9 });
    s.lines.ema21.applyOptions({ visible: visible.ema21 });
    s.lines.ema50.applyOptions({ visible: visible.ema50 });
    s.lines.vwap.applyOptions({ visible: visible.vwap });
    for (const k of ["bb_upper", "bb_mid", "bb_lower"]) s.lines[k].applyOptions({ visible: visible.bb });
  }, [visible]);

  const shown = legend ?? latest;

  return (
    <div>
      <div className="mb-2 flex flex-wrap items-center gap-1.5" role="group" aria-label="เส้นบนกราฟ">
        {OVERLAYS.map((o) => (
          <button
            key={o.key}
            onClick={() => setVisible((v) => ({ ...v, [o.key]: !v[o.key] }))}
            aria-pressed={visible[o.key]}
            className={`inline-flex items-center gap-1.5 rounded-md border border-line px-2 py-1 text-xs transition-opacity ${
              visible[o.key] ? "bg-surface-2 text-ink" : "text-muted opacity-60"
            }`}
          >
            <span
              aria-hidden
              className="inline-block h-0 w-4"
              style={{ borderTop: `2px ${o.dashed ? "dashed" : "solid"} ${o.color}` }}
            />
            {o.label}
            {shown && o.key !== "bb" && (
              <span className="tabular text-ink-2">{fmtPrice(shown.values[o.key])}</span>
            )}
          </button>
        ))}
      </div>
      {shown && (
        <p className="tabular mb-1 text-xs text-ink-2">
          <span className="text-muted">
            {dayMonth(shown.time, ET)} {hhmm(shown.time, ET)} ET · {hhmm(shown.time, BKK)} ไทย
          </span>{" "}
          O {fmtPrice(shown.o)} H {fmtPrice(shown.h)} L {fmtPrice(shown.l)} C {fmtPrice(shown.c)}
          <span className="text-muted"> · RSI </span>
          {shown.values.rsi14?.toFixed(1) ?? "–"}
          <span className="text-muted"> · MACD </span>
          {shown.values.macd?.toFixed(3) ?? "–"} / {shown.values.signal?.toFixed(3) ?? "–"}
        </p>
      )}
      <div className="relative">
        <div ref={box} className="h-[460px] w-full sm:h-[560px]" aria-label={`กราฟแท่งเทียน ${symbol}`} />
        {(error || empty) && (
          <div className="absolute inset-0 flex items-center justify-center bg-surface/70 text-sm text-ink-2">
            {error ?? "ยังไม่มีข้อมูลแท่งเทียน"}
          </div>
        )}
      </div>
    </div>
  );
}
