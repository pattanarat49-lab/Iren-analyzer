import { clockPart, datePart, fmtPct, fmtPrice, fmtSigned, MODE_TH, SESSION_TH } from "@/lib/format";
import type { Link, StreamState } from "@/lib/useMarketStream";
import type { ConnectionMode, Session } from "@/lib/types";

const sessionDot: Record<Session, string> = {
  pre: "bg-s1",
  regular: "bg-up",
  after: "bg-s4",
  closed: "bg-muted",
};

function connectionLabel(link: Link, mode: ConnectionMode | undefined): { text: string; tone: string } {
  if (link === "offline") return { text: "ติดต่อเซิร์ฟเวอร์ไม่ได้", tone: "text-down" };
  if (link === "connecting" && !mode) return { text: "กำลังเชื่อมต่อ…", tone: "text-ink-2" };
  const m = mode ?? "starting";
  const tone = m === "live" ? "text-up" : m === "error" ? "text-down" : m === "demo" || m === "polling" ? "text-warn" : "text-ink-2";
  const suffix = link === "polling" ? " · สำรองผ่าน REST" : "";
  return { text: MODE_TH[m] + suffix, tone };
}

export function PriceHeader({ s }: { s: StreamState }) {
  const sym = s.status?.primary_symbol ?? "IREN";
  const q = s.quotes[sym];
  const change = q?.change ?? null;
  const dir = change == null ? "" : change > 0 ? "text-up" : change < 0 ? "text-down" : "text-ink-2";
  const arrow = change == null ? "" : change > 0 ? "▲" : change < 0 ? "▼" : "";
  const session = s.market?.session;
  const conn = connectionLabel(s.link, s.status?.mode);

  return (
    <header className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-xs">
        {session && (
          <span className="inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 font-medium">
            <span className={`h-2 w-2 rounded-full ${sessionDot[session]}`} aria-hidden />
            {SESSION_TH[session]}
            {s.market?.is_half_day && <span className="text-warn">· ปิดครึ่งวัน</span>}
          </span>
        )}
        <span className={`inline-flex items-center gap-1.5 rounded-full border border-line bg-surface px-2.5 py-1 font-medium ${conn.tone}`}>
          <span className="h-2 w-2 rounded-full bg-current" aria-hidden />
          {conn.text}
        </span>
        {s.status?.stock_feed === "iex" && (
          <span className="rounded-full border border-line bg-surface px-2.5 py-1 text-ink-2" title="แผนฟรีของ Alpaca ส่งข้อมูลจากตลาด IEX เท่านั้น ราคาถูกต้อง แต่ปริมาณซื้อขายเป็นเพียงบางส่วนของตลาด">
            Feed: IEX
          </span>
        )}
      </div>

      {s.status?.mode === "demo" && (
        <p className="rounded-lg border border-warn/40 bg-warn/10 px-3 py-2 text-sm text-warn">
          ⚠ กำลังแสดง<strong>ข้อมูลจำลอง</strong> เพราะยังไม่ได้ตั้งค่า Alpaca API key ตัวเลขทั้งหมดไม่ใช่ราคาจริง
        </p>
      )}
      {s.status?.mode === "error" && s.status.detail && (
        <p className="rounded-lg border border-down/40 bg-down/10 px-3 py-2 text-sm text-down">⚠ {s.status.detail}</p>
      )}
      {q?.halted && (
        <p className="rounded-lg border border-down/40 bg-down/10 px-3 py-2 text-sm font-medium text-down">
          ⏸ {sym} ถูกหยุดพักการซื้อขาย {q.halt_reason && `– ${q.halt_reason}`}
        </p>
      )}

      <div className="flex flex-wrap items-end justify-between gap-x-6 gap-y-2">
        <div>
          <div className="flex items-baseline gap-2">
            <h1 className="text-lg font-bold">{sym}</h1>
            <span className="text-sm text-muted">IREN Limited · NASDAQ</span>
          </div>
          <div className="flex flex-wrap items-baseline gap-x-3">
            <span className="tabular text-4xl font-semibold tracking-tight sm:text-5xl">${fmtPrice(q?.price)}</span>
            <span className={`tabular text-lg font-medium ${dir}`}>
              {arrow} {fmtSigned(change)} ({fmtPct(q?.change_pct)})
            </span>
          </div>
          {q?.after_hours_change != null && (
            <p className="tabular text-sm text-ink-2">
              นอกเวลาทำการ: {fmtSigned(q.after_hours_change)} ({fmtPct(q.after_hours_change_pct)}) จากราคาปิดวันนี้
            </p>
          )}
          <p className="text-xs text-muted">
            เทียบราคาปิดก่อนหน้า ${fmtPrice(q?.prev_close)}
            {q?.bid != null && q?.ask != null && (
              <span className="tabular"> · Bid {fmtPrice(q.bid)} / Ask {fmtPrice(q.ask)}</span>
            )}
          </p>
        </div>

        <dl className="tabular grid grid-cols-[auto_auto] gap-x-3 gap-y-0.5 text-xs">
          <dt className="text-muted">อัปเดตล่าสุด</dt>
          <dd className="text-ink-2">
            {clockPart(q?.updated?.et)} ET · {clockPart(q?.updated?.bkk)} น.
          </dd>
          <dt className="text-muted">เวลาตอนนี้ (ET)</dt>
          <dd className="text-ink-2">
            {datePart(s.serverTime?.et)} {clockPart(s.serverTime?.et)}
          </dd>
          <dt className="text-muted">เวลาไทย</dt>
          <dd className="text-ink-2">
            {datePart(s.serverTime?.bkk)} {clockPart(s.serverTime?.bkk)} น.
          </dd>
          {s.market && (
            <>
              <dt className="text-muted">{session === "regular" ? "ตลาดปิด" : "ตลาดเปิดครั้งถัดไป"}</dt>
              <dd className="text-ink-2">
                {session === "regular"
                  ? `${clockPart(s.market.next_regular_close.et)} ET · ${clockPart(s.market.next_regular_close.bkk)} น.`
                  : `${datePart(s.market.next_regular_open.bkk)} ${clockPart(s.market.next_regular_open.bkk)} น. (ไทย)`}
              </dd>
            </>
          )}
        </dl>
      </div>
    </header>
  );
}
