"use client";

import { History } from "lucide-react";

type HistoryButtonProps = {
  onPress?: () => void;
  isDisabled?: boolean;
  compact?: boolean;
  className?: string;
};

export function HistoryButton({ onPress, isDisabled = false, compact = false, className = "" }: HistoryButtonProps) {
  if (compact) {
    return (
      <button
        type="button"
        onClick={onPress}
        disabled={isDisabled || !onPress}
        className={`inline-flex items-center gap-1.5 rounded-full border border-cyber-blue/50 bg-white px-3 py-1.5 font-display text-xs font-bold text-cyber-strong shadow-xs hover:border-cyber-blue hover:bg-blue-50/60 transition-all cursor-pointer disabled:opacity-40 shrink-0 ${className}`}
        aria-label="เปิดประวัติการสนทนา"
      >
        <History className="size-4 text-cyber-blue" />
        <span className="hidden min-[420px]:inline">ประวัติ</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={onPress}
      disabled={isDisabled || !onPress}
      className={`inline-flex items-center gap-2 rounded-full border-2 border-cyber-blue bg-white px-5 py-2.5 font-display text-sm font-bold text-cyber-strong shadow-xs hover:bg-blue-50/60 hover:shadow-sm transition-all cursor-pointer disabled:opacity-40 shrink-0 ${className}`}
      aria-label="เปิดประวัติการสนทนา"
    >
      <History className="size-4.5 text-cyber-blue" />
      <span>History</span>
    </button>
  );
}
