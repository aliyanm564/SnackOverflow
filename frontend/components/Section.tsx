import type { ReactNode } from "react";

type SectionProps = {
  title: string;
  description?: string;
  icon?: ReactNode;
  children: ReactNode;
};

export function Section({ title, description, icon, children }: SectionProps) {
  return (
    <section className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[var(--shadow)] backdrop-blur-sm">
      <div className="mb-5 flex items-start gap-3">
        {icon ? (
          <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--accent-muted)] text-[var(--accent)]">
            {icon}
          </div>
        ) : null}
        <div>
          <h2 className="font-display text-lg font-semibold tracking-tight text-[var(--text)]">
            {title}
          </h2>
          {description ? (
            <p className="mt-1 text-sm text-[var(--text-muted)]">{description}</p>
          ) : null}
        </div>
      </div>
      {children}
    </section>
  );
}
