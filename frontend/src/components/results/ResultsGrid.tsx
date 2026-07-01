"use client";

import { ModeCard } from "./ModeCard";
import type { ModeInfo } from "@/lib/types";

interface Props {
  results: Record<string, string>;
  modes: ModeInfo[];
}

export function ResultsGrid({ results, modes }: Props) {
  const modeMap = new Map(modes.map((m) => [m.key, m]));

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full max-w-6xl mx-auto">
      {Object.entries(results).map(([key, content], i) => {
        const meta = modeMap.get(key);
        return (
          <ModeCard
            key={key}
            icon={meta?.icon ?? "\u{1F4AC}"}
            label={meta?.label ?? key}
            content={content}
            index={i}
          />
        );
      })}
    </div>
  );
}
