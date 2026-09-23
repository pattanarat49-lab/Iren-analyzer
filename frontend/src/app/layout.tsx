import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "IREN Analyzer",
  description: "วิเคราะห์หุ้น IREN แบบเรียลไทม์ และประมาณความน่าจะเป็นที่ราคาจะขึ้นหรือลง (เพื่อการศึกษาเท่านั้น)",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#0d0d0d",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="th" className="h-full antialiased">
      <body className="min-h-full bg-page font-sans text-ink">{children}</body>
    </html>
  );
}
