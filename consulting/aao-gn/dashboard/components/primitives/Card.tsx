import { HTMLAttributes, ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padding?: "sm" | "md" | "lg" | "none";
}

export function Card({
  children,
  padding = "md",
  className = "",
  ...rest
}: CardProps) {
  const pad =
    padding === "none"
      ? ""
      : padding === "sm"
      ? "p-4"
      : padding === "lg"
      ? "p-7"
      : "p-5";
  return (
    <div
      className={`rounded-xl border border-ink-200 bg-white dark:border-ink-800 dark:bg-ink-900/40 ${pad} ${className}`}
      {...rest}
    >
      {children}
    </div>
  );
}
