import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "GEO 진단 리포트",
  description: "AI 챗봇 답변에서 우리 브랜드가 얼마나 언급·추천되는지 진단합니다.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko">
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
