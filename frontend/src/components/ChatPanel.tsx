/**
 * ChatPanel —— 右栏：自然语言追问 + 流式回答.
 *
 * Day 7 接 Vercel AI SDK 的 useChat hook 后，这里渲染 messages + 输入框.
 * 当前 Day 5 是壳，仅占位 + 显示已就绪状态.
 */

"use client";

import { Send } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";

export function ChatPanel() {
  return (
    <div className="flex h-full flex-col">
      {/* 头部 */}
      <div className="flex h-12 items-center border-b border-border px-4">
        <div className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
          对话
        </div>
      </div>

      {/* 消息流（Day 7 实接） */}
      <ScrollArea className="flex-1 px-4 py-4">
        <div className="flex flex-col items-center justify-center gap-3 pt-12 text-center">
          <div className="text-sm text-muted-foreground">
            选个股票后，在下方提问。
          </div>
          <div className="text-[11px] text-muted-foreground/70">
            v0.1 day 5 壳：流式回答 + Citation drawer 在 Day 7-8 接入
          </div>
        </div>
      </ScrollArea>

      {/* 输入框 */}
      <form
        className="flex items-center gap-2 border-t border-border px-3 py-3"
        onSubmit={(e) => {
          e.preventDefault();
          // Day 7：调用 useChat().sendMessage
        }}
      >
        <Input
          name="message"
          placeholder="问一个问题..."
          disabled
          className="flex-1"
        />
        <Button type="submit" size="icon" disabled>
          <Send className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
