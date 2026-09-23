import type { ReactNode } from "react";
import { SIGNAL_ICON, SIGNAL_TH } from "@/lib/format";
import type { Signal } from "@/lib/types";

export function Card({ title, right, children, className = "" }: { title?: ReactNode; right?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`rounded-xl border border-line bg-surface p-4 ${className}`}>
      {(title || right) && (
        <header className="mb-3 flex items-center justify-between gap-2">
          {title && <h2 className="text-sm font-semibold text-ink-2">{title}</h2>}
          {right}
        </header>
      )}
      {children}
    </section>
  );
}

const signalClass: Record<Signal, string> = {
  bullish: "text-up border-up/40 bg-up/10",
  bearish: "text-down border-down/40 bg-down/10",
  neutral: "text-ink-2 border-line bg-surface-2",
};

/** Signal badge: always icon + Thai label, never colour alone. */
export function SignalBadge({ signal, small = false }: { signal: Signal; small?: boolean }) {
  return (
    <span
      className={`inline-flex shrink-0 items-center gap-1 rounded-full border font-medium ${signalClass[signal]} ${
        small ? "px-1.5 py-0 text-[11px]" : "px-2 py-0.5 text-xs"
      }`}
    >
      <span aria-hidden>{SIGNAL_ICON[signal]}</span>
      {SIGNAL_TH[signal]}
    </span>
  );
}

export function Segmented<T extends string | number>({
  options,
  value,
  onChange,
  label,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex rounded-lg border border-line bg-surface-2 p-0.5">
      {options.map((o) => (
        <button
          key={String(o.value)}
          role="radio"
          aria-checked={o.value === value}
          onClick={() => onChange(o.value)}
          className={`rounded-md px-2.5 py-1 text-xs font-medium transition-colors ${
            o.value === value ? "bg-ink text-page" : "text-ink-2 hover:bg-white/5"
          }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
