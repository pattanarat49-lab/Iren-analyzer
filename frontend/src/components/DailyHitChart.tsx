"use client";

import { useState } from "react";

type Day = { day: string; n: number; hit_rate: number };

const W = 320;
const H = 140;
const M = { l: 36, r: 8, t: 8, b: 22 };

/** Daily hit rate as bars around the 50% coin-flip line. */
export function DailyHitChart({ days }: { days: Day[] }) {
  const [hover, setHover] = useState<number | null>(null);
  const data = days.slice(-30);
  const iw = W - M.l - M.r;
  const ih = H - M.t - M.b;
  const bw = data.length ? iw / data.length : iw;
  const y = (v: number) => M.t + (1 - v) * ih;
  const h = hover != null ? data[hover] : null;
  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-[420px]" role="img" aria-label="อัตราทายถูกรายวัน">
        {[0, 0.5, 1].map((t) => (
          <g key={t}>
            <line x1={M.l} x2={W - M.r} y1={y(t)} y2={y(t)} stroke={t === 0.5 ? "var(--muted)" : "var(--grid)"} strokeDasharray={t === 0.5 ? "4 4" : undefined} />
            <text x={M.l - 6} y={y(t) + 4} textAnchor="end" fontSize="10" fill="var(--muted)">
              {t * 100}%
            </text>
          </g>
        ))}
        {data.map((d, i) => {
          const top = y(d.hit_rate);
          const barH = Math.max(1, y(0) - top);
          return (
            <g key={d.day} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)}>
              <rect x={M.l + i * bw} y={M.t} width={bw} height={ih} fill="transparent" />
              <rect
                x={M.l + i * bw + 1}
                y={top}
                width={Math.max(1, bw - 2)}
                height={barH}
                rx={Math.min(4, bw / 3)}
                fill={d.hit_rate >= 0.5 ? "var(--up)" : "var(--down-mark)"}
                opacity={hover == null || hover === i ? 0.9 : 0.5}
              />
            </g>
          );
        })}
        {data.length > 0 && (
          <>
            <text x={M.l} y={H - 6} fontSize="10" fill="var(--muted)">{data[0].day.slice(5)}</text>
            <text x={W - M.r} y={H - 6} textAnchor="end" fontSize="10" fill="var(--muted)">{data[data.length - 1].day.slice(5)}</text>
          </>
        )}
      </svg>
      {h && (
        <div className="tabular pointer-events-none absolute right-2 top-0 rounded-md border border-line bg-page/95 px-2 py-1 text-xs">
          <div className="text-muted">{h.day}</div>
          <div>ทายถูก {(h.hit_rate * 100).toFixed(1)}%</div>
          <div className="text-muted">{h.n} ครั้ง</div>
        </div>
      )}
    </div>
  );
}
