import { ReactNode } from "react";

type Tone =
  | "neutral"
  | "accent"
  | "win"
  | "loss"
  | "draw"
  | "warn"
  | "danger"
  | "muted";

interface PillProps {
  children: ReactNode;
  tone?: Tone;
  size?: "xs" | "sm";
}

const TONES: Record<Tone, string> = {
  neutral: "bg-ink-100 text-ink-700 dark:bg-ink-800 dark:text-ink-200",
  accent: "bg-accent-soft text-accent dark:bg-accent/15 dark:text-accent",
  win: "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400",
  loss: "bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-400",
  draw: "bg-ink-100 text-ink-600 dark:bg-ink-800 dark:text-ink-300",
  warn: "bg-amber-50 text-amber-800 dark:bg-amber-500/10 dark:text-amber-400",
  danger: "bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-300",
  muted: "bg-transparent text-ink-500 dark:text-ink-400 border border-ink-200 dark:border-ink-700",
};

export function Pill({ children, tone = "neutral", size = "sm" }: PillProps) {
  const cls = TONES[tone];
  const sz = size === "xs" ? "text-[10px] px-1.5 py-0.5" : "text-xs px-2 py-0.5";
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full font-medium tabular-nums ${sz} ${cls}`}
    >
      {children}
    </span>
  );
}
