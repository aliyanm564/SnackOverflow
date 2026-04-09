import type { MenuItem } from "@/lib/types";
import { Clock } from "lucide-react";

function formatPrice(value: number | null): string {
  if (value === null || value === undefined) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(value);
}

/** API returns ISO-like time strings e.g. "14:30:00" or full ISO; show local-friendly time. */
function formatTime(value: string | null | undefined): string | null {
  if (!value) return null;
  const trimmed = value.trim();
  if (!trimmed) return null;
  if (/^\d{1,2}:\d{2}(:\d{2})?/.test(trimmed)) {
    const [h, m] = trimmed.split(":");
    const hour = parseInt(h, 10);
    const minute = parseInt(m, 10);
    if (Number.isNaN(hour) || Number.isNaN(minute)) return trimmed.slice(0, 8);
    const d = new Date();
    d.setHours(hour, minute, 0, 0);
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
    }).format(d);
  }
  const d = new Date(trimmed);
  if (!Number.isNaN(d.getTime())) {
    return new Intl.DateTimeFormat("en-US", {
      hour: "numeric",
      minute: "2-digit",
    }).format(d);
  }
  return trimmed.slice(0, 8);
}

function availabilityLabel(
  from: string | null | undefined,
  until: string | null | undefined
): { text: string; emphasis: boolean } {
  const a = formatTime(from ?? null);
  const b = formatTime(until ?? null);
  if (a && b) return { text: `${a} – ${b}`, emphasis: true };
  if (a) return { text: `From ${a}`, emphasis: true };
  if (b) return { text: `Until ${b}`, emphasis: true };
  return { text: "No serving hours set", emphasis: false };
}

type Props = {
  item: MenuItem;
  /** Smaller card for nested restaurant menu lists */
  compact?: boolean;
};

export function MenuItemCard({ item, compact }: Props) {
  const { text: hoursText, emphasis: hoursEmphasis } = availabilityLabel(
    item.available_from,
    item.available_until
  );

  return (
    <article
      className={`group relative overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface-elevated)] transition hover:border-[var(--accent)]/35 hover:shadow-[0_0_0_1px_var(--accent-glow)] ${
        compact ? "p-4" : "p-5"
      }`}
    >
      <div className="absolute -right-8 -top-8 h-24 w-24 rounded-full bg-[var(--accent)]/10 blur-2xl transition group-hover:bg-[var(--accent)]/20" />
      <div className="relative">
        <div className="flex items-start justify-between gap-3">
          <h3
            className={`font-display font-semibold leading-snug text-[var(--text)] ${
              compact ? "text-base" : "text-lg"
            }`}
          >
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

        <div
          className={`mt-3 flex items-start gap-2 rounded-lg border px-3 py-2 ${
            hoursEmphasis
              ? "border-[var(--accent)]/30 bg-[var(--accent-muted)]"
              : "border-[var(--border)] bg-[var(--input-bg)]/50"
          }`}
        >
          <Clock
            className={`mt-0.5 h-4 w-4 shrink-0 ${
              hoursEmphasis ? "text-[var(--accent)]" : "text-[var(--text-subtle)]"
            }`}
            strokeWidth={1.75}
          />
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-[var(--text-subtle)]">
              Available
            </p>
            <p
              className={`text-sm ${
                hoursEmphasis ? "font-medium text-[var(--text)]" : "text-[var(--text-muted)]"
              }`}
            >
              {hoursText}
            </p>
          </div>
        </div>

        {!compact ? (
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
        ) : null}
      </div>
    </article>
  );
}
