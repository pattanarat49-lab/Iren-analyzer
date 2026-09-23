"use client";

import { Card, Segmented } from "./ui";

export type Horizon = "5m" | "15m" | "1h" | "eod";

export const HORIZONS: { value: Horizon; label: string }[] = [
  { value: "5m", label: "5 นาที" },
  { value: "15m", label: "15 นาที" },
  { value: "1h", label: "1 ชั่วโมง" },
  { value: "eod", label: "จบวัน" },
];

/** Semicircle split into P(up) (left→) and P(down). Values are null until the model is available. */
function Arc({ pUp }: { pUp: number | null }) {
  const r = 80;
  const cx = 100;
  const cy = 95;
  const point = (frac: number) => {
    const a = Math.PI * (1 - frac);
    return [cx + r * Math.cos(a), cy - r * Math.sin(a)];
  };
  const arc = (from: number, to: number) => {
    const [x1, y1] = point(from);
    const [x2, y2] = point(to);
    return `M ${x1} ${y1} A ${r} ${r} 0 0 1 ${x2} ${y2}`;
  };
  const gap = 0.012; // 2px-ish surface gap between the two segments
  return (
    <svg viewBox="0 0 200 110" className="w-full max-w-[280px]" role="img" aria-label={pUp == null ? "ยังไม่มีค่าความน่าจะเป็น" : `โอกาสขึ้น ${Math.round(pUp * 100)}%`}>
      {pUp == null ? (
        <path d={arc(0, 1)} stroke="var(--grid)" strokeWidth="16" fill="none" strokeLinecap="round" />
      ) : (
        <>
          <path d={arc(0, Math.max(0, pUp - gap))} stroke="var(--up)" strokeWidth="16" fill="none" strokeLinecap="round" />
          <path d={arc(Math.min(1, pUp + gap), 1)} stroke="var(--down-mark)" strokeWidth="16" fill="none" strokeLinecap="round" />
        </>
      )}
      <line x1={cx} y1={cy - r - 12} x2={cx} y2={cy - r + 12} stroke="var(--muted)" strokeWidth="1" strokeDasharray="2 2" />
    </svg>
  );
}

export function ProbabilityGauge({
  horizon,
  onHorizon,
  pUp,
}: {
  horizon: Horizon;
  onHorizon: (h: Horizon) => void;
  pUp: number | null;
}) {
  const up = pUp == null ? null : Math.round(pUp * 100);
  return (
    <Card title="โอกาสราคาขึ้น vs ลง">
      <div className="mb-3 flex justify-center">
        <Segmented label="ช่วงเวลาทำนาย" options={HORIZONS} value={horizon} onChange={onHorizon} />
      </div>
      <div className="flex flex-col items-center">
        <Arc pUp={pUp} />
        <div className="-mt-10 grid w-full max-w-[300px] grid-cols-2 text-center">
          <div>
            <div className="tabular text-4xl font-bold text-up">{up == null ? "–" : `${up}%`}</div>
            <div className="text-sm text-ink-2">▲ ขึ้น</div>
          </div>
          <div>
            <div className="tabular text-4xl font-bold text-down">{up == null ? "–" : `${100 - up}%`}</div>
            <div className="text-sm text-ink-2">▼ ลง</div>
          </div>
        </div>
      </div>
      {pUp == null && (
        <p className="mt-3 rounded-lg bg-surface-2 px-3 py-2 text-center text-xs text-ink-2">
          โมเดลความน่าจะเป็นจะเปิดใช้ใน Phase 4 (ต้องฝึกด้วยข้อมูลจริงย้อนหลัง 2 ปีก่อน) ตอนนี้จึงยังไม่แสดงตัวเลข
        </p>
      )}
      <p className="mt-2 text-center text-[11px] text-muted">
        &quot;ขึ้น&quot; = ราคา ณ สิ้นช่วงเวลาสูงกว่าราคาปัจจุบัน · ความน่าจะเป็นเป็นค่าประมาณ ไม่ใช่การรับประกัน
      </p>
    </Card>
  );
}
