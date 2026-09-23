import { fmtCorr, fmtFrac, fmtPct, fmtPrice } from "@/lib/format";
import type { Analysis, Quote } from "@/lib/types";
import { Card, SignalBadge } from "./ui";

export function ContextPanel({ analysis, quotes, primary }: { analysis: Analysis | null; quotes: Record<string, Quote>; primary: string }) {
  const rows = analysis && analysis.ready ? analysis.relative : [];
  return (
    <Card title={`${primary} เทียบกับหุ้น/สินทรัพย์ที่เกี่ยวข้อง`}>
      {rows.length === 0 ? (
        <p className="text-sm text-ink-2">กำลังโหลด…</p>
      ) : (
        <ul className="space-y-2">
          {rows.map((r) => {
            const q = quotes[r.symbol];
            const pct = q?.change_pct ?? (r.change_today != null ? r.change_today * 100 : null);
            const tone = pct == null ? "text-ink-2" : pct > 0 ? "text-up" : pct < 0 ? "text-down" : "text-ink-2";
            return (
              <li key={r.symbol} className="rounded-lg bg-surface-2 p-3">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-baseline gap-2">
                    <span className="font-semibold">{r.symbol}</span>
                    <span className="tabular text-sm text-ink-2">${fmtPrice(q?.price ?? r.price)}</span>
                    <span className={`tabular text-sm ${tone}`}>{fmtPct(pct)}</span>
                  </div>
                  <SignalBadge signal={r.signal} small />
                </div>
                <dl className="tabular mt-1.5 grid grid-cols-3 gap-1 text-xs">
                  <div>
                    <dt className="text-muted">Corr 1 ชม.</dt>
                    <dd>{fmtCorr(r.corr_60)}</dd>
                  </div>
                  <div>
                    <dt className="text-muted">Corr 1 วัน</dt>
                    <dd>{fmtCorr(r.corr_390)}</dd>
                  </div>
                  <div>
                    <dt className="text-muted">RS วันนี้</dt>
                    <dd>{fmtFrac(r.rs_today)}</dd>
                  </div>
                </dl>
                <p className="mt-1.5 text-xs leading-relaxed text-ink-2">{r.explanation}</p>
              </li>
            );
          })}
        </ul>
      )}
      <p className="mt-2 text-[11px] text-muted">
        Corr = ความสัมพันธ์ของผลตอบแทนราย 1 นาที (−1 ถึง +1) · RS = {primary} แข็ง/อ่อนกว่าตัวเทียบกี่ % นับจากราคาปิดก่อนหน้า
      </p>
    </Card>
  );
}
