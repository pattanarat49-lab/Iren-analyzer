"use client";

import Link from "next/link";
import type { Horizon } from "@/lib/types";
import { useTrackRecord } from "@/lib/useTrackRecord";
import { TrackStats } from "./TrackStats";
import { Card } from "./ui";

export function TrackRecordPanel({ horizon }: { horizon: Horizon }) {
  const { data, error } = useTrackRecord(30);
  const h = data?.horizons[horizon];
  return (
    <Card
      title={`ผลงานจริงของการทำนาย (${h?.label ?? horizon}, 30 วัน)`}
      right={
        <Link href="/track-record" className="text-xs text-s1 hover:underline">
          ดูทั้งหมด →
        </Link>
      }
    >
      {error && !data && <p className="text-sm text-ink-2">โหลดผลงานย้อนหลังไม่สำเร็จ</p>}
      {!error && !data && <p className="text-sm text-ink-2">กำลังโหลด…</p>}
      {h && (h.n === 0 ? (
        <p className="text-sm text-ink-2">
          ยังไม่มีผลที่ออกแล้ว ระบบบันทึกการทำนายทุก 1 นาทีและรอดูราคาจริงเมื่อครบเวลา
          {h.pending > 0 && ` (รอผลอยู่ ${h.pending.toLocaleString("en-US")} ครั้ง)`}
        </p>
      ) : (
        <TrackStats h={h} />
      ))}
      {data?.source === "demo" && <p className="mt-2 text-[11px] text-warn">ผลงานนี้มาจากข้อมูลจำลอง</p>}
    </Card>
  );
}
