"use client";

import Link from "next/link";
import { useState } from "react";
import { clockPart, datePart, fmtPrice } from "@/lib/format";
import { useTrackRecord } from "@/lib/useTrackRecord";
import type { Horizon, RetrainStatus } from "@/lib/types";
import { CalibrationChart } from "./CalibrationChart";
import { DailyHitChart } from "./DailyHitChart";
import { Disclaimer } from "./Disclaimer";
import { TrackStats } from "./TrackStats";
import { Card, Segmented } from "./ui";

const ORDER: Horizon[] = ["5m", "15m", "1h", "eod"];
const RANGES = [
  { value: 7, label: "7 วัน" },
  { value: 30, label: "30 วัน" },
  { value: 90, label: "90 วัน" },
];

const RETRAIN_TH: Record<RetrainStatus["state"], string> = {
  idle: "พร้อม",
  running: "กำลังฝึกโมเดลใหม่…",
  ok: "ฝึกล่าสุดสำเร็จ",
  failed: "ฝึกล่าสุดล้มเหลว",
};

export function TrackRecordView() {
  const [days, setDays] = useState(30);
  const { data, error } = useTrackRecord(days);

  return (
    <>
      <main className="mx-auto max-w-7xl space-y-4 px-4 pb-24 pt-4 lg:px-6">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <Link href="/" className="text-xs text-s1 hover:underline">
              ← กลับหน้าหลัก
            </Link>
            <h1 className="text-xl font-bold">ผลงานจริงของการทำนาย IREN</h1>
            <p className="text-sm text-ink-2">
              ทุก 1 นาทีระบบบันทึกความน่าจะเป็นของแต่ละช่วงเวลา แล้วเทียบกับราคาจริงเมื่อครบเวลา ข้อมูลในหน้านี้ไม่ได้ผ่านการคัดเลือก
            </p>
          </div>
          <Segmented label="ช่วงเวลาย้อนหลัง" options={RANGES} value={days} onChange={setDays} />
        </div>

        {data?.source === "demo" && (
          <p className="rounded-lg border border-warn/40 bg-warn/10 px-3 py-2 text-sm text-warn">⚠ ผลงานนี้มาจากข้อมูลจำลอง ไม่ใช่ผลกับราคาจริง</p>
        )}
        {error && !data && <p className="text-sm text-down">โหลดข้อมูลไม่สำเร็จ ตรวจสอบว่า backend ทำงานอยู่</p>}

        {data && (
          <Card title="การฝึกโมเดลใหม่อัตโนมัติ">
            <p className="text-sm">
              {data.retrain.enabled ? RETRAIN_TH[data.retrain.state] : "ปิดอยู่"}
              {data.retrain.next_run && (
                <span className="text-ink-2">
                  {" "}
                  · รอบถัดไป {datePart(data.retrain.next_run.bkk)} {clockPart(data.retrain.next_run.bkk)} น. (ไทย) / {clockPart(data.retrain.next_run.et)} ET
                </span>
              )}
            </p>
            <p className="mt-1 text-xs text-muted">ฝึกใหม่ทุกวันทำการ 30 นาทีหลังตลาดช่วงหลังปิด (after-hours) จบ โดยใช้ข้อมูลล่าสุดทั้งหมด</p>
            {data.retrain.state === "failed" && <pre className="mt-2 overflow-x-auto whitespace-pre-wrap text-xs text-down">{data.retrain.last_message}</pre>}
          </Card>
        )}

        <div className="grid gap-4 lg:grid-cols-2">
          {data &&
            ORDER.map((hk) => {
              const h = data.horizons[hk];
              return (
                <Card key={hk} title={`ช่วงเวลา ${h.label}`}>
                  {h.n === 0 ? (
                    <p className="text-sm text-ink-2">
                      ยังไม่มีผลที่ออกแล้ว{h.pending > 0 && ` (รอผล ${h.pending.toLocaleString("en-US")} ครั้ง)`}
                    </p>
                  ) : (
                    <div className="space-y-4">
                      <TrackStats h={h} />
                      <div>
                        <h3 className="mb-1 text-xs font-semibold text-ink-2">Calibration: ทาย X% แล้วขึ้นจริงกี่ %</h3>
                        <CalibrationChart bins={h.calibration ?? []} />
                      </div>
                      <div>
                        <h3 className="mb-1 text-xs font-semibold text-ink-2">อัตราทายถูกรายวัน (เส้นประ = 50%)</h3>
                        <DailyHitChart days={h.daily ?? []} />
                      </div>
                      <details>
                        <summary className="cursor-pointer text-xs text-ink-2">การทำนายล่าสุด {h.recent?.length ?? 0} ครั้ง</summary>
                        <div className="mt-2 overflow-x-auto">
                          <table className="tabular w-full text-xs">
                            <thead className="text-muted">
                              <tr>
                                <th className="py-1 text-left font-normal">เวลา (ไทย)</th>
                                <th className="text-right font-normal">โอกาสขึ้น</th>
                                <th className="text-right font-normal">ราคา → ผล</th>
                                <th className="text-right font-normal">ผล</th>
                              </tr>
                            </thead>
                            <tbody>
                              {h.recent?.map((r) => (
                                <tr key={r.made_at.utc} className="border-t border-line">
                                  <td className="py-1">{datePart(r.made_at.bkk).slice(5)} {clockPart(r.made_at.bkk).slice(0, 5)}</td>
                                  <td className="text-right">{(r.p_up * 100).toFixed(0)}%</td>
                                  <td className="text-right">
                                    {fmtPrice(r.price)} → {fmtPrice(r.outcome_price)}
                                  </td>
                                  <td className={`text-right ${r.hit ? "text-up" : "text-down"}`}>{r.hit ? "✓ ถูก" : "✗ ผิด"}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </details>
                      <details>
                        <summary className="cursor-pointer text-xs text-ink-2">ตาราง calibration</summary>
                        <table className="tabular mt-2 w-full text-xs">
                          <thead className="text-muted">
                            <tr>
                              <th className="py-1 text-left font-normal">ช่วงที่ทาย</th>
                              <th className="text-right font-normal">ทายเฉลี่ย</th>
                              <th className="text-right font-normal">ขึ้นจริง</th>
                              <th className="text-right font-normal">จำนวน</th>
                            </tr>
                          </thead>
                          <tbody>
                            {h.calibration?.map((b) => (
                              <tr key={b.bin_low} className="border-t border-line">
                                <td className="py-1">
                                  {Math.round(b.bin_low * 100)}–{Math.round(b.bin_high * 100)}%
                                </td>
                                <td className="text-right">{(b.mean_p * 100).toFixed(1)}%</td>
                                <td className="text-right">{(b.observed * 100).toFixed(1)}%</td>
                                <td className="text-right">{b.n.toLocaleString("en-US")}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </details>
                    </div>
                  )}
                </Card>
              );
            })}
        </div>
      </main>
      <Disclaimer />
    </>
  );
}
