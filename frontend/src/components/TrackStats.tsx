import type { TrackHorizon } from "@/lib/types";

const VERDICT = {
  better: { tone: "text-up", text: "▲ ผลจริงดีกว่าการเดาแบบง่ายอย่างมีนัยสำคัญ (Brier, ความเชื่อมั่น 95%)" },
  worse: { tone: "text-down", text: "▼ ผลจริงแย่กว่าการเดาแบบง่ายอย่างมีนัยสำคัญ" },
  no_difference: { tone: "text-down", text: "● ผลจริงยังไม่ต่างจากการเดาแบบง่ายอย่างมีนัยสำคัญ (no proven edge)" },
  insufficient: { tone: "text-warn", text: "● ข้อมูลผลจริงยังไม่พอจะสรุปว่ามีความได้เปรียบ" },
} as const;

const pct = (x: number | undefined | null) => (x == null ? "–" : `${(x * 100).toFixed(1)}%`);

/** Hit rate and Brier score of live predictions vs the naive baseline. */
export function TrackStats({ h }: { h: TrackHorizon }) {
  return (
    <>
      <dl className="tabular grid grid-cols-3 gap-2 text-center text-xs">
        <div className="rounded-lg bg-surface-2 p-2">
          <dt className="text-muted">ทายถูก</dt>
          <dd className="text-sm font-semibold">{pct(h.hit_rate)}</dd>
          <dd className="text-muted">เดาง่าย {pct(h.baseline_hit_rate)}</dd>
        </div>
        <div className="rounded-lg bg-surface-2 p-2">
          <dt className="text-muted">Brier (ต่ำ = ดี)</dt>
          <dd className="text-sm font-semibold">{h.brier?.toFixed(4) ?? "–"}</dd>
          <dd className="text-muted">เดาง่าย {h.baseline_brier?.toFixed(4) ?? "–"}</dd>
        </div>
        <div className="rounded-lg bg-surface-2 p-2">
          <dt className="text-muted">ผลออกแล้ว</dt>
          <dd className="text-sm font-semibold">{h.n.toLocaleString("en-US")}</dd>
          <dd className="text-muted">รอผล {h.pending.toLocaleString("en-US")}</dd>
        </div>
      </dl>
      {h.n > 0 && h.n < 100 && (
        <p className="mt-2 text-[12px] text-warn">⚠ ผลที่ออกแล้วยังน้อย (&lt;100 ครั้ง) ตัวเลขยังผันผวนมาก อย่าเพิ่งสรุป</p>
      )}
      {h.n >= 100 && h.verdict && (
        <p className={`mt-2 text-[12px] ${VERDICT[h.verdict].tone}`}>
          {VERDICT[h.verdict].text}
          {h.verdict === "insufficient" && ` (มี ${h.n_days ?? 0} วัน ต้องมีอย่างน้อย 20 วัน)`}
        </p>
      )}
    </>
  );
}
