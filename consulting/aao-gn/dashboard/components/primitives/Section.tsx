import { ReactNode } from "react";

interface SectionProps {
  id: string;
  title: string;
  caption?: string;
  action?: ReactNode;
  children: ReactNode;
}

export function Section({ id, title, caption, action, children }: SectionProps) {
  return (
    <section id={id} className="scroll-mt-20">
      <div className="mb-5 flex items-end justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight text-ink-900 dark:text-ink-50">
            {title}
          </h2>
          {caption ? (
            <p className="mt-1 text-sm text-ink-500 dark:text-ink-400">{caption}</p>
          ) : null}
        </div>
        {action ? <div className="shrink-0">{action}</div> : null}
      </div>
      {children}
    </section>
  );
}
