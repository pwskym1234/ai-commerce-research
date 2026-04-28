"use client";

import { useEffect, useState } from "react";
import { SECTIONS } from "@/lib/constants";

export function SectionNav() {
  const [active, setActive] = useState<string>(SECTIONS[0].id);

  useEffect(() => {
    const els = SECTIONS.map(({ id }) => document.getElementById(id)).filter(
      Boolean,
    ) as HTMLElement[];
    if (!els.length) return;
    const obs = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
        if (visible[0]) setActive(visible[0].target.id);
      },
      { rootMargin: "-30% 0px -55% 0px", threshold: [0, 0.25, 0.5, 0.75, 1] },
    );
    els.forEach((el) => obs.observe(el));
    return () => obs.disconnect();
  }, []);

  return (
    <nav className="no-print sticky top-6 hidden lg:block">
      <ul className="space-y-0.5 text-sm">
        {SECTIONS.map(({ id, label }) => (
          <li key={id}>
            <a
              href={`#${id}`}
              className={`block rounded-md px-3 py-1.5 transition ${
                active === id
                  ? "bg-ink-100 font-medium text-ink-900 dark:bg-ink-800 dark:text-ink-100"
                  : "text-ink-500 hover:text-ink-900 dark:text-ink-400 dark:hover:text-ink-100"
              }`}
            >
              {label}
            </a>
          </li>
        ))}
      </ul>
    </nav>
  );
}
