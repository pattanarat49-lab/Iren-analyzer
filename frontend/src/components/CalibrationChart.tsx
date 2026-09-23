"use client";

import { useState } from "react";
import type { CalibrationBin } from "@/lib/types";

const W = 320;
const H = 260;
const M = { l: 44, r: 20, t: 12, b: 40 };
const iw = W - M.l - M.r;
const ih = H - M.t - M.b;
const x = (v: number) => M.l + v * iw;
const y = (v: number) => M.t + (1 - v) * ih;
const TICKS = [0, 0.25, 0.5, 0.75, 1];

/** Reliability diagram: predicted P(up) vs how often "up" actually happened. Dots on the
 *  dashed diagonal = well calibrated. Dot area grows with the number of predictions. */
export function CalibrationChart({ bins }: { bins: CalibrationBin[] }) {
  const [hover, setHover] = useState<number | null>(null);
  const maxN = Math.max(1, ...bins.map((b) => b.n));
  const h = hover != null ? bins[hover] : null;
  return (
    <div className="relative">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full max-w-[420px]" role="img" aria-label="กราฟ calibration: ความน่าจะเป็นที่ทาย เทียบกับสัดส่วนที่ขึ้นจริง">
        {TICKS.map((t) => (
          <g key={t}>
            <line x1={x(0)} x2={x(1)} y1={y(t)} y2={y(t)} stroke="var(--grid)" strokeWidth="1" />
            <text x={M.l - 6} y={y(t) + 4} textAnchor="end" fontSize="10" fill="var(--muted)" className="tabular">
              {Math.round(t * 100)}%
            </text>
            <text x={x(t)} y={H - M.b + 16} textAnchor="middle" fontSize="10" fill="var(--muted)" className="tabular">
              {Math.round(t * 100)}%
            </text>
          </g>
        ))}
        <line x1={x(0)} y1={y(0)} x2={x(1)} y2={y(1)} stroke="var(--muted)" strokeDasharray="4 4" strokeWidth="1" />
        <text x={x(0.98)} y={y(0.98) + 14} textAnchor="end" fontSize="10" fill="var(--muted)">
          ตรงพอดี
        </text>
        <text x={M.l + iw / 2} y={H - 4} textAnchor="middle" fontSize="11" fill="var(--ink-2)">
          โอกาสขึ้นที่โมเดลทาย
        </text>
        <text x={12} y={M.t + ih / 2} textAnchor="middle" fontSize="11" fill="var(--ink-2)" transform={`rotate(-90 12 ${M.t + ih / 2})`}>
          ขึ้นจริง
        </text>
        {bins.map((b, i) => {
          const r = Math.max(4, Math.sqrt(b.n / maxN) * 12);
          return (
            <g key={i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} onFocus={() => setHover(i)} onBlur={() => setHover(null)} tabIndex={0}>
              <circle cx={x(b.mean_p)} cy={y(b.observed)} r={r + 8} fill="transparent" />
              <circle cx={x(b.mean_p)} cy={y(b.observed)} r={r} fill="var(--s1)" stroke="var(--surface)" strokeWidth="2" opacity={hover == null || hover === i ? 1 : 0.5} />
            </g>
          );
        })}
      </svg>
      {h && (
        <div className="tabular pointer-events-none absolute right-2 top-2 rounded-md border border-line bg-page/95 px-2 py-1 text-xs">
          <div className="text-muted">
            ช่วง {Math.round(h.bin_low * 100)}–{Math.round(h.bin_high * 100)}%
          </div>
          <div>ทายเฉลี่ย {(h.mean_p * 100).toFixed(1)}%</div>
          <div>ขึ้นจริง {(h.observed * 100).toFixed(1)}%</div>
          <div className="text-muted">{h.n.toLocaleString("en-US")} ครั้ง</div>
        </div>
      )}
    </div>
  );
}
