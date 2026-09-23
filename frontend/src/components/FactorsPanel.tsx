import type { Factor, HorizonPrediction } from "@/lib/types";
import { Card } from "./ui";

function FactorList({ items, dir }: { items: Factor[]; dir: "up" | "down" }) {
  const max = Math.max(...items.map((i) => Math.abs(i.impact)), 1e-9);
  if (items.length === 0) return <p className="text-xs text-muted">ไม่มี</p>;
  return (
    <ul className="space-y-2">
      {items.map((f) => (
        <li key={f.feature}>
          <div className="flex items-baseline justify-between gap-2 text-[13px]">
            <span>{f.label}</span>
            <span className="tabular shrink-0 text-xs text-ink-2">{f.value}</span>
          </div>
          <div className="mt-1 h-1.5 w-full rounded-full bg-surface-2">
            <div
              className={`h-1.5 rounded-full ${dir === "up" ? "bg-up" : "bg-down"}`}
              style={{ width: `${Math.max(4, (Math.abs(f.impact) / max) * 100)}%` }}
            />
          </div>
        </li>
      ))}
    </ul>
  );
}

export function FactorsPanel({ prediction }: { prediction: HorizonPrediction | undefined }) {
  if (!prediction?.available) {
    return (
      <Card title="ปัจจัยที่มีผลต่อการประมาณ">
        <p className="text-sm text-ink-2">จะแสดงเมื่อมีโมเดลสำหรับช่วงเวลานี้</p>
      </Card>
    );
  }
  const method = prediction.model === "lgbm" ? "SHAP (TreeSHAP ของ LightGBM)" : "ค่าสัมประสิทธิ์ × ค่าปัจจุบัน (Logistic Regression)";
  return (
    <Card title={`ปัจจัยที่มีผลต่อการประมาณ (${prediction.label})`}>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <h3 className="mb-2 text-xs font-semibold text-up">▲ ดันให้ขึ้น</h3>
          <FactorList items={prediction.factors.up} dir="up" />
        </div>
        <div>
          <h3 className="mb-2 text-xs font-semibold text-down">▼ กดให้ลง</h3>
          <FactorList items={prediction.factors.down} dir="down" />
        </div>
      </div>
      <p className="mt-3 text-[11px] text-muted">
        ความยาวแถบ = น้ำหนักเทียบกันของแต่ละปัจจัยต่อผลลัพธ์ของโมเดล คำนวณด้วย {method} · ไม่ได้แปลว่าเป็นสาเหตุ
      </p>
    </Card>
  );
}
