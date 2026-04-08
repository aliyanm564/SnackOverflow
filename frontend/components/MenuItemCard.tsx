import type { MenuItem } from "@/lib/types";

function formatPrice(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

function formatTime(value: string | null | undefined): string {
  if (!value) return "—";
  return value.slice(0, 5);
}

type Props = {
  item: MenuItem;
};

export function MenuItemCard({ item }: Props) {
  return (
    <article className="group relative overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface-elevated)] p-5 transition hover:border-[var(--accent)]/35 hover:shadow-[0_0_0_1px_var(--accent-glow)]">
      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-[var(--accent)]/10 blur-2xl transition group-hover:bg-[var(--accent)]/20" />
      <div className="relative">
        <div className="flex items-start justify-between gap-3">
          <h3 className="font-display text-lg font-semibold leading-snug text-[var(--text)]">
            {item.name}
          </h3>
          <span className="shrink-0 rounded-lg bg-[var(--accent-muted)] px-2.5 py-1 font-mono text-sm font-semibold tabular-nums text-[var(--accent)]">
            {formatPrice(item.price)}
          </span>
        </div>
        <p className="mt-2 text-sm text-[var(--text-muted)]">
          <span className="text-[var(--text-subtle)]">Category</span>{" "}
          {item.category ?? "Uncategorized"}
        </p>
        {(item.available_from || item.available_until) && (
          <p className="mt-1 text-xs text-[var(--text-subtle)]">
            Available {formatTime(item.available_from ?? null)} –{" "}
            {formatTime(item.available_until ?? null)}
          </p>
        )}
        <dl className="mt-4 grid gap-1 text-xs text-[var(--text-subtle)]">
          <div className="flex justify-between gap-2">
            <dt className="font-medium text-[var(--text-muted)]">Item ID</dt>
            <dd className="truncate font-mono">{item.food_item_id}</dd>
          </div>
          <div className="flex justify-between gap-2">
            <dt className="font-medium text-[var(--text-muted)]">Restaurant</dt>
            <dd className="truncate font-mono">{item.restaurant_id}</dd>
          </div>
        </dl>
      </div>
    </article>
  );
}
