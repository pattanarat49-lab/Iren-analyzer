/** Permanent disclaimer, fixed to the bottom of every screen. */
export function Disclaimer() {
  return (
    <div
      role="note"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-warn/30 bg-page/95 px-4 py-2 text-center text-[12px] leading-snug text-warn backdrop-blur"
    >
      ⚠️ เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำทางการเงิน · ความน่าจะเป็นเป็นเพียงการประมาณการ ไม่ใช่การรับประกัน
    </div>
  );
}
