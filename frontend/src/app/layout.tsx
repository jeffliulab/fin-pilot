import type { Metadata } from "next";
import localFont from "next/font/local";

import "./globals.css";
import { ThreePaneLayout } from "@/components/ThreePaneLayout";
import { LeftMenu } from "@/components/LeftMenu";
import { ChatPanel } from "@/components/ChatPanel";
import { CitationDrawer } from "@/components/CitationDrawer";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "FinPilot · 金融版 Cursor",
  description:
    "三栏 AI 工作台：左菜单选模块（个股 / 行业 / 市场），中工作区沉淀分析卡片，右聊天追问。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <ThreePaneLayout
          left={<LeftMenu />}
          center={children}
          right={<ChatPanel />}
        />
        <CitationDrawer />
      </body>
    </html>
  );
}
