import type { Analysis } from "@/lib/types";
import { Card, SignalBadge } from "./ui";

export function IndicatorPanel({ analysis, tf }: { analysis: Analysis | null; tf: number }) {
  if (!analysis || !analysis.ready) {
    return (
      <Card title="สัญญาณจากอินดิเคเตอร์">
        <p className="text-sm text-ink-2">{analysis && !analysis.ready ? analysis.message : "กำลังโหลด…"}</p>
      </Card>
    );
  }
  const { summary } = analysis;
  return (
    <Card
      title={`สัญญาณจากอินดิเคเตอร์ (แท่ง ${tf} นาที)`}
      right={<span className="text-[11px] text-muted">คำนวณใหม่ทุกแท่งเทียน</span>}
    >
      <div className="mb-3 flex items-start gap-2 rounded-lg bg-surface-2 p-3">
        <SignalBadge signal={summary.overall} />
        <div className="text-sm">
          <p>{summary.explanation}</p>
          <p className="tabular mt-0.5 text-xs text-muted">
            บวก {summary.counts.bullish} · ลบ {summary.counts.bearish} · กลาง {summary.counts.neutral}
          </p>
        </div>
      </div>
      <ul className="divide-y divide-line">
        {analysis.indicators.map((i) => (
          <li key={i.key} className="py-2.5">
            <div className="flex items-center justify-between gap-2">
              <span className="text-sm font-medium">{i.name}</span>
              <span className="flex items-center gap-2">
                <span className="tabular text-sm text-ink-2">{i.display}</span>
                <SignalBadge signal={i.signal} small />
              </span>
            </div>
            <p className="mt-0.5 text-[13px] leading-relaxed text-ink-2">{i.explanation}</p>
          </li>
        ))}
      </ul>
      {analysis.iex_only && (
        <p className="mt-2 text-[11px] text-muted">
          * VWAP และ Relative Volume คำนวณจากปริมาณซื้อขายของตลาด IEX เท่านั้น (แผนข้อมูลฟรี)
        </p>
      )}
    </Card>
  );
}
