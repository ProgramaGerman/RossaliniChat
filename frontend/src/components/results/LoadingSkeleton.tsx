export function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 w-full max-w-6xl mx-auto">
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="p-5 rounded-2xl border border-zinc-200 dark:border-zinc-800 bg-white dark:bg-zinc-900 animate-pulse"
        >
          <div className="flex items-center gap-3 mb-3">
            <div className="w-8 h-8 rounded-full bg-zinc-200 dark:bg-zinc-700" />
            <div className="h-5 w-28 rounded bg-zinc-200 dark:bg-zinc-700" />
          </div>
          <div className="space-y-2">
            <div className="h-3 w-full rounded bg-zinc-200 dark:bg-zinc-700" />
            <div className="h-3 w-3/4 rounded bg-zinc-200 dark:bg-zinc-700" />
            <div className="h-3 w-5/6 rounded bg-zinc-200 dark:bg-zinc-700" />
          </div>
        </div>
      ))}
    </div>
  );
}
