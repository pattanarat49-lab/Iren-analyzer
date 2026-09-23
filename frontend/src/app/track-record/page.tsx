import type { Metadata } from "next";
import { TrackRecordView } from "@/components/TrackRecordView";

export const metadata: Metadata = {
  title: "IREN Track Record",
  description: "ผลงานจริงของการทำนาย: อัตราทายถูกและกราฟ calibration",
};

export default function Page() {
  return <TrackRecordView />;
}
