"use client";

import { clampPct } from "@/lib/format";

interface DonutProps {
  value: number;
  size?: number;
  stroke?: number;
  color?: string;
  trackColor?: string;
}

export function Donut({
  value,
  size = 64,
  stroke = 6,
  color = "var(--accent)",
  trackColor = "var(--border)",
}: DonutProps) {
  const v = clampPct(value);
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const dash = (v / 100) * c;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={trackColor}
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke={color}
        strokeWidth={stroke}
        strokeDasharray={`${dash} ${c - dash}`}
        strokeDashoffset={c / 4}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transform: `rotate(-90deg)`, transformOrigin: `${size / 2}px ${size / 2}px` }}
      />
    </svg>
  );
}
