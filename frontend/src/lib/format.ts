import type { ConnectionMode, Session, Signal } from "./types";

export function fmtPrice(p: number | null | undefined): string {
  if (p == null || !Number.isFinite(p)) return "–";
  if (p >= 1000) return p.toLocaleString("en-US", { maximumFractionDigits: 0 });
  return p.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: p < 1 ? 4 : 2 });
}

export function fmtSigned(x: number | null | undefined, digits = 2): string {
  if (x == null || !Number.isFinite(x)) return "–";
  const s = Math.abs(x).toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
  return `${x > 0 ? "+" : x < 0 ? "−" : ""}${s}`;
}

/** Percent from a percentage number (e.g. 2.5 -> "+2.50%"). */
export function fmtPct(x: number | null | undefined, digits = 2): string {
  return x == null || !Number.isFinite(x) ? "–" : `${fmtSigned(x, digits)}%`;
}

/** Percent from a fraction (e.g. 0.025 -> "+2.50%"). */
export function fmtFrac(x: number | null | undefined, digits = 2): string {
  return x == null || !Number.isFinite(x) ? "–" : fmtPct(x * 100, digits);
}

export function fmtCorr(x: number | null | undefined): string {
  return x == null || !Number.isFinite(x) ? "–" : fmtSigned(x, 2);
}

/** "2026-09-23 09:30:05 EDT" -> "09:30:05" */
export function clockPart(s: string | undefined | null): string {
  if (!s) return "–";
  const m = s.match(/\d{2}:\d{2}(:\d{2})?/);
  return m ? m[0] : s;
}

export function datePart(s: string | undefined | null): string {
  if (!s) return "";
  const m = s.match(/\d{4}-\d{2}-\d{2}/);
  return m ? m[0] : "";
}

export const SIGNAL_TH: Record<Signal, string> = {
  bullish: "บวก",
  bearish: "ลบ",
  neutral: "กลาง",
};

export const SIGNAL_ICON: Record<Signal, string> = {
  bullish: "▲",
  bearish: "▼",
  neutral: "●",
};

export const SESSION_TH: Record<Session, string> = {
  pre: "ก่อนตลาดเปิด",
  regular: "ตลาดเปิด",
  after: "หลังตลาดปิด",
  closed: "ตลาดปิด",
};

export const MODE_TH: Record<ConnectionMode, string> = {
  starting: "กำลังเชื่อมต่อ",
  live: "เรียลไทม์",
  polling: "ดึงข้อมูลเป็นระยะ",
  demo: "ข้อมูลจำลอง",
  error: "เชื่อมต่อไม่ได้",
};

/** Unix seconds -> "HH:MM" in a time zone. */
export function hhmm(sec: number, tz: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone: tz, hour: "2-digit", minute: "2-digit", hour12: false }).format(
    new Date(sec * 1000),
  );
}

export function dayMonth(sec: number, tz: string): string {
  return new Intl.DateTimeFormat("en-GB", { timeZone: tz, day: "2-digit", month: "short" }).format(new Date(sec * 1000));
}
