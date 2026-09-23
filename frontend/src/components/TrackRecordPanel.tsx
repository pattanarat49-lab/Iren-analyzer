import { Card } from "./ui";

export function TrackRecordPanel() {
  return (
    <Card title="ผลงานย้อนหลังของการทำนาย">
      <p className="text-sm text-ink-2">
        จะเริ่มบันทึกผลทำนายทุก 1 นาทีต่อช่วงเวลา แล้วเทียบกับราคาจริงที่เกิดขึ้น (อัตราทายถูก + กราฟ calibration) ใน Phase 5
      </p>
    </Card>
  );
}
