"use client";

import { useEffect, useState } from "react";
import { backendUrl } from "@/lib/config";
import type { Analysis } from "@/lib/types";
import { useMarketStream } from "@/lib/useMarketStream";
import { ContextPanel } from "./ContextPanel";
import { Disclaimer } from "./Disclaimer";
import { FactorsPanel } from "./FactorsPanel";
import { IndicatorPanel } from "./IndicatorPanel";
import { PriceChart } from "./PriceChart";
import { PriceHeader } from "./PriceHeader";
import { ProbabilityGauge, type Horizon } from "./ProbabilityGauge";
import { TrackRecordPanel } from "./TrackRecordPanel";
import { Card, Segmented } from "./ui";

const TIMEFRAMES = [
  { value: 1, label: "1 นาที" },
  { value: 5, label: "5 นาที" },
  { value: 15, label: "15 นาที" },
];

export function Dashboard() {
  const s = useMarketStream();
  const primary = s.status?.primary_symbol ?? "IREN";
  const [tf, setTf] = useState(1);
  const [horizon, setHorizon] = useState<Horizon>("15m");
  const [tfAnalysis, setTfAnalysis] = useState<Analysis | null>(null);
  const barSeq = s.barSeq[primary] ?? 0;

  // 1-minute analysis arrives over the WebSocket; 5/15-minute is fetched when a new bar lands.
  useEffect(() => {
    if (tf === 1) return;
    const ctrl = new AbortController();
    fetch(`${backendUrl()}/api/analysis?tf=${tf}`, { cache: "no-store", signal: ctrl.signal })
      .then((r) => (r.ok ? r.json() : null))
      .then((a) => a && setTfAnalysis(a))
      .catch(() => undefined);
    return () => ctrl.abort();
  }, [tf, barSeq]);

  const analysis = tf === 1 ? s.analysis : tfAnalysis;
  const pred = s.prediction?.horizons[horizon];

  return (
    <>
      <main className="mx-auto max-w-7xl space-y-4 px-4 pb-24 pt-4 lg:px-6">
        <PriceHeader s={s} />

        <div className="grid gap-4 lg:grid-cols-12">
          <div className="space-y-4 lg:col-span-8">
            <div className="lg:hidden">
              <ProbabilityGauge horizon={horizon} onHorizon={setHorizon} prediction={pred} />
            </div>
            <Card
              title="กราฟราคา"
              right={<Segmented label="ขนาดแท่งเทียน" options={TIMEFRAMES} value={tf} onChange={setTf} />}
            >
              <PriceChart symbol={primary} tf={tf} refreshKey={barSeq} forming={s.quotes[primary]?.forming_bar} />
            </Card>
            <FactorsPanel prediction={pred} />
            <IndicatorPanel analysis={analysis} tf={tf} />
          </div>

          <div className="space-y-4 lg:col-span-4">
            <div className="hidden lg:block">
              <ProbabilityGauge horizon={horizon} onHorizon={setHorizon} prediction={pred} />
            </div>
            <ContextPanel analysis={s.analysis} quotes={s.quotes} primary={primary} />
            <TrackRecordPanel horizon={horizon} />
          </div>
        </div>
      </main>
      <Disclaimer />
    </>
  );
}
