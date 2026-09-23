"use client";

import { fmtPrice } from "@/lib/format";
import type { Horizon, HorizonPrediction } from "@/lib/types";
import { Card, Segmented } from "./ui";

export type { Horizon };

export const HORIZONS: { value: Horizon; label: string }[] = [
  { value: "5m", label: "5 นาที" },
  { value: "15m", label: "15 นาที" },
  { value: "1h", label: "1 ชั่วโมง" },
  { value: "eod", label: "จบวัน" },
];

const MODEL_NAME = { logreg: "Logistic Regression", lgbm: "LightGBM" } as const;

/** Semicircle split into P(up) (left) and P(down) (right). */
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
  const gap = 0.012;
  return (
    <svg
      viewBox="0 0 200 110"
      className="w-full max-w-[280px]"
      role="img"
      aria-label={pUp == null ? "ยังไม่มีค่าความน่าจะเป็น" : `โอกาสขึ้น ${Math.round(pUp * 100)}% โอกาสลง ${100 - Math.round(pUp * 100)}%`}
    >
      {pUp == null ? (
        <path d={arc(0, 1)} stroke="var(--grid)" strokeWidth="16" fill="none" strokeLinecap="round" />
      ) : (
        <>
          <path d={arc(0, Math.max(0.001, pUp - gap))} stroke="var(--up)" strokeWidth="16" fill="none" strokeLinecap="round" />
          <path d={arc(Math.min(0.999, pUp + gap), 1)} stroke="var(--down-mark)" strokeWidth="16" fill="none" strokeLinecap="round" />
        </>
      )}
      <line x1={cx} y1={cy - r - 12} x2={cx} y2={cy - r + 12} stroke="var(--muted)" strokeWidth="1" strokeDasharray="2 2" />
    </svg>
  );
}

function pct(x: number, digits = 1) {
  return `${(x * 100).toFixed(digits)}%`;
}

export function ProbabilityGauge({
  horizon,
  onHorizon,
  prediction,
}: {
  horizon: Horizon;
  onHorizon: (h: Horizon) => void;
  prediction: HorizonPrediction | undefined;
}) {
  const ok = prediction?.available ? prediction : null;
  const pUp = ok ? ok.p_up : null;
  const up = pUp == null ? null : Math.round(pUp * 100);

  return (
    <Card title="โอกาสราคาขึ้น vs ลง">
      <div className="mb-3 flex justify-center">
        <Segmented label="ช่วงเวลาทำนาย" options={HORIZONS} value={horizon} onChange={onHorizon} />
      </div>

      <div className="flex flex-col items-center">
        <Arc pUp={pUp} />
        <div className="mt-1 grid w-full max-w-[300px] grid-cols-2 text-center">
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

      {!ok && (
        <p className="mt-3 rounded-lg bg-surface-2 px-3 py-2 text-center text-xs text-ink-2">
          {prediction && !prediction.available ? prediction.reason : "กำลังโหลดโมเดล…"}
        </p>
      )}

      {ok && !ok.edge && (
        <div role="alert" className="mt-3 rounded-lg border border-down/50 bg-down/10 px-3 py-2 text-sm text-down">
          <p className="font-semibold">⚠ ยังไม่พิสูจน์ว่ามีความได้เปรียบ (no proven edge)</p>
          <p className="mt-0.5 text-[13px] text-ink-2">
            {ok.edge_reason} ตัวเลขนี้จึง<strong className="text-ink">ไม่ควร</strong>ถือว่าดีกว่าการเดาแบบสุ่ม
          </p>
        </div>
      )}
      {ok && ok.edge && (
        <p className="mt-3 rounded-lg border border-up/40 bg-up/10 px-3 py-2 text-[13px] text-ink-2">
          ✓ {ok.edge_reason} (ผลในอดีตไม่รับประกันอนาคต)
        </p>
      )}
      {ok?.source === "demo" && (
        <p className="mt-2 rounded-lg border border-warn/40 bg-warn/10 px-3 py-1.5 text-[12px] text-warn">
          โมเดลนี้ฝึกจากข้อมูลจำลอง ใช้ดูการทำงานของระบบเท่านั้น
        </p>
      )}

      {ok?.expected_move && (
        <div className="mt-3 rounded-lg bg-surface-2 px-3 py-2 text-sm">
          <p className="text-xs text-muted">ช่วงแกว่งที่คาดไว้ใน {ok.label} (±ATR ปรับตามเวลา)</p>
          <p className="tabular">
            ${fmtPrice(ok.expected_move.low)} – ${fmtPrice(ok.expected_move.high)}{" "}
            <span className="text-ink-2">(±{ok.expected_move.move_pct.toFixed(2)}%)</span>
          </p>
        </div>
      )}

      {ok && (
        <dl className="tabular mt-3 grid grid-cols-3 gap-2 text-center text-xs">
          <div className="rounded-lg bg-surface-2 p-2">
            <dt className="text-muted">ความแม่นยำ</dt>
            <dd className="text-sm font-semibold">{pct(ok.metrics.accuracy)}</dd>
            <dd className="text-muted">เดาง่าย {pct(ok.metrics.baseline_accuracy)}</dd>
          </div>
          <div className="rounded-lg bg-surface-2 p-2">
            <dt className="text-muted">Brier (ต่ำ = ดี)</dt>
            <dd className="text-sm font-semibold">{ok.metrics.brier.toFixed(4)}</dd>
            <dd className="text-muted">เดาง่าย {ok.metrics.baseline_brier.toFixed(4)}</dd>
          </div>
          <div className="rounded-lg bg-surface-2 p-2">
            <dt className="text-muted">ทดสอบย้อนหลัง</dt>
            <dd className="text-sm font-semibold">{ok.metrics.n_test_days} วัน</dd>
            <dd className="text-muted">{ok.metrics.n_test.toLocaleString("en-US")} ครั้ง</dd>
          </div>
        </dl>
      )}

      <p className="mt-2 text-center text-[11px] leading-relaxed text-muted">
        {ok && (
          <>
            โมเดล {MODEL_NAME[ok.model]} · ปรับเทียบแบบ {ok.calibration} · ฝึกเมื่อ {ok.trained_at.slice(0, 16).replace("T", " ")} UTC
            <br />
          </>
        )}
        &quot;ขึ้น&quot; = ราคา ณ สิ้นช่วงเวลาสูงกว่าราคาปัจจุบัน · &quot;เดาง่าย&quot; = ทายตามสัดส่วนขึ้น/ลงในอดีต · ตัวเลขทดสอบทั้งหมดเป็นแบบ
        out-of-sample (walk-forward)
      </p>
    </Card>
  );
}
