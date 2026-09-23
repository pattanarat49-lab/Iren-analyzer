"use client";

import { Disclaimer } from "@/components/Disclaimer";

/** Shown if a component crashes, instead of a blank page. */
export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <>
      <main className="mx-auto max-w-xl space-y-3 px-4 pt-16 text-center">
        <h1 className="text-lg font-bold">เกิดข้อผิดพลาดในการแสดงผล</h1>
        <p className="text-sm text-ink-2">ข้อมูลบางส่วนอาจไม่ครบหรือรูปแบบไม่ถูกต้อง ลองโหลดใหม่อีกครั้ง</p>
        <p className="text-xs text-muted">{error.message}</p>
        <button onClick={reset} className="rounded-lg bg-ink px-4 py-2 text-sm font-medium text-page">
          ลองใหม่
        </button>
      </main>
      <Disclaimer />
    </>
  );
}
