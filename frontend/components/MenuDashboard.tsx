"use client";

import {
  filterMenu,
  fetchRestaurantMenu,
  login,
  searchMenu,
} from "@/lib/api";
import {
  getStoredApiBase,
  getStoredToken,
  setStoredApiBase,
  setStoredToken,
} from "@/lib/storage";
import type { MenuItem } from "@/lib/types";
import {
  Filter,
  Loader2,
  LogIn,
  Search,
  Server,
  Store,
  UtensilsCrossed,
} from "lucide-react";
import { useEffect, useState } from "react";
import { MenuItemCard } from "./MenuItemCard";
import { Section } from "./Section";

const DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export function MenuDashboard() {
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [restaurantId, setRestaurantId] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [category, setCategory] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");

  const [items, setItems] = useState<MenuItem[]>([]);
  const [lastLoaded, setLastLoaded] = useState<MenuItem[]>([]);
  const [status, setStatus] = useState<string>("Sign in, then load a menu or search.");
  const [loading, setLoading] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setApiBase(getStoredApiBase(DEFAULT_API_BASE));
    setToken(getStoredToken());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    setStoredApiBase(apiBase);
    setStoredToken(token);
  }, [hydrated, apiBase, token]);

  const run = async (label: string, fn: () => Promise<void>) => {
    setLoading(true);
    setStatus(label);
    try {
      await fn();
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    run("Signing you in…", async () => {
      const data = await login(apiBase, email.trim(), password);
      setToken(data.access_token);
      setStatus("Signed in. Your token is saved in this browser.");
    });
  };

  const handleLoadMenu = (e: React.FormEvent) => {
    e.preventDefault();
    const id = restaurantId.trim();
    if (!id) {
      setStatus("Enter a restaurant ID.");
      return;
    }
    run("Loading menu…", async () => {
      const list = await fetchRestaurantMenu(apiBase, token, id);
      setItems(list);
      setLastLoaded(list);
      setStatus(`Loaded ${list.length} item(s) for this restaurant.`);
    });
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const q = searchQuery.trim();
    if (!q) {
      setItems(lastLoaded);
      setStatus("Search empty — showing the last loaded menu.");
      return;
    }
    run("Searching…", async () => {
      const list = await searchMenu(apiBase, token, q);
      setItems(list);
      setStatus(`Found ${list.length} match(es).`);
    });
  };

  const handleFilter = (e: React.FormEvent) => {
    e.preventDefault();
    run("Filtering…", async () => {
      const list = await filterMenu(apiBase, token, {
        category: category.trim() || undefined,
        minPrice: minPrice.trim() || undefined,
        maxPrice: maxPrice.trim() || undefined,
      });
      setItems(list);
      setStatus(`Filter returned ${list.length} item(s).`);
    });
  };

  const inputClass =
    "w-full rounded-xl border border-[var(--border)] bg-[var(--input-bg)] px-4 py-3 text-sm text-[var(--text)] placeholder:text-[var(--text-subtle)] outline-none transition focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/25";

  const btnPrimaryClass =
    "inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-strong)] px-5 py-3 text-sm font-semibold text-[var(--accent-foreground)] shadow-lg shadow-[var(--accent)]/20 transition hover:brightness-110 disabled:opacity-50";

  const btnSecondaryClass =
    "inline-flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-[var(--surface-elevated)] px-5 py-3 text-sm font-medium text-[var(--text)] transition hover:border-[var(--accent)]/40 hover:bg-[var(--surface)] disabled:opacity-50";

  return (
    <div className="mx-auto max-w-5xl px-4 pb-20 pt-10 sm:px-6 lg:px-8">
      <header className="mb-12 text-center sm:mb-14">
        <p className="mb-2 font-mono text-xs uppercase tracking-[0.2em] text-[var(--accent)]">
          SnackOverflow
        </p>
        <h1 className="font-display text-4xl font-semibold tracking-tight text-[var(--text)] sm:text-5xl">
          Menu studio
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-pretty text-base text-[var(--text-muted)]">
          Connect to your API, browse menus by restaurant, and explore search and filters
          with a layout built for clarity.
        </p>
      </header>

      <div
        className={`mb-8 flex flex-col gap-3 rounded-2xl border px-5 py-4 sm:flex-row sm:items-center sm:justify-between ${
          loading
            ? "border-[var(--accent)]/30 bg-[var(--accent-muted)]"
            : "border-[var(--border)] bg-[var(--surface)]"
        }`}
        role="status"
        aria-live="polite"
      >
        <div className="flex items-center gap-3 text-sm text-[var(--text-muted)]">
          {loading ? (
            <Loader2 className="h-5 w-5 shrink-0 animate-spin text-[var(--accent)]" />
          ) : null}
          <span className="text-[var(--text)]">{status}</span>
        </div>
        {token ? (
          <span className="rounded-full bg-emerald-500/15 px-3 py-1 text-xs font-medium text-emerald-400">
            Authenticated
          </span>
        ) : (
          <span className="rounded-full bg-amber-500/15 px-3 py-1 text-xs font-medium text-amber-400">
            Not signed in
          </span>
        )}
      </div>

      <div className="flex flex-col gap-6">
        <Section
          title="API connection"
          description="Point the app at your running SnackOverflow backend."
          icon={<Server className="h-5 w-5" strokeWidth={1.75} />}
        >
          <label className="block text-sm font-medium text-[var(--text-muted)]">
            Base URL
          </label>
          <input
            className={`${inputClass} mt-2 font-mono text-xs sm:text-sm`}
            value={apiBase}
            onChange={(e) => setApiBase(e.target.value)}
            placeholder="http://localhost:8000/api/v1"
            spellCheck={false}
          />
        </Section>

        <Section
          title="Sign in"
          description="JWT is stored locally in your browser for API calls."
          icon={<LogIn className="h-5 w-5" strokeWidth={1.75} />}
        >
          <form onSubmit={handleLogin} className="flex flex-col gap-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <input
                className={inputClass}
                type="email"
                autoComplete="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <input
                className={inputClass}
                type="password"
                autoComplete="current-password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>
            <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
              <div className="min-w-0 flex-1">
                <label className="block text-sm font-medium text-[var(--text-muted)]">
                  Access token
                </label>
                <textarea
                  className={`${inputClass} mt-2 min-h-[88px] resize-y font-mono text-xs`}
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="Paste a token or sign in above"
                  spellCheck={false}
                />
              </div>
              <button type="submit" className={btnPrimaryClass} disabled={loading}>
                <LogIn className="h-4 w-4" />
                Sign in
              </button>
            </div>
          </form>
        </Section>

        <div className="grid gap-6 lg:grid-cols-2">
          <Section
            title="Restaurant menu"
            description="Load all items for one restaurant."
            icon={<Store className="h-5 w-5" strokeWidth={1.75} />}
          >
            <form onSubmit={handleLoadMenu} className="flex flex-col gap-3 sm:flex-row">
              <input
                className={inputClass}
                value={restaurantId}
                onChange={(e) => setRestaurantId(e.target.value)}
                placeholder="Restaurant ID"
                required
              />
              <button type="submit" className={`${btnPrimaryClass} shrink-0`} disabled={loading}>
                <UtensilsCrossed className="h-4 w-4" />
                Load menu
              </button>
            </form>
          </Section>

          <Section
            title="Search"
            description="Search item names across every restaurant."
            icon={<Search className="h-5 w-5" strokeWidth={1.75} />}
          >
            <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
              <input
                className={inputClass}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="e.g. burger, salad…"
              />
              <button type="submit" className={`${btnSecondaryClass} shrink-0`} disabled={loading}>
                <Search className="h-4 w-4" />
                Search
              </button>
            </form>
          </Section>
        </div>

        <Section
          title="Filters"
          description="Filter by category, or min and max price together."
          icon={<Filter className="h-5 w-5" strokeWidth={1.75} />}
        >
          <form
            onSubmit={handleFilter}
            className="flex flex-col gap-3 sm:flex-row sm:flex-wrap"
          >
            <input
              className={`${inputClass} sm:min-w-[160px] sm:flex-1`}
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Category"
            />
            <input
              className={`${inputClass} sm:w-32`}
              type="number"
              step="0.01"
              min={0}
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
              placeholder="Min $"
            />
            <input
              className={`${inputClass} sm:w-32`}
              type="number"
              step="0.01"
              min={0}
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
              placeholder="Max $"
            />
            <button type="submit" className={`${btnSecondaryClass} sm:shrink-0`} disabled={loading}>
              <Filter className="h-4 w-4" />
              Apply
            </button>
          </form>
        </Section>

        <section>
          <h2 className="mb-4 font-display text-xl font-semibold text-[var(--text)]">
            Results
            {items.length > 0 ? (
              <span className="ml-2 font-sans text-sm font-normal text-[var(--text-muted)]">
                {items.length} item{items.length === 1 ? "" : "s"}
              </span>
            ) : null}
          </h2>
          {items.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)]/50 px-8 py-16 text-center">
              <UtensilsCrossed
                className="mx-auto mb-4 h-10 w-10 text-[var(--text-subtle)]"
                strokeWidth={1.25}
              />
              <p className="text-[var(--text-muted)]">
                No items yet. Sign in and load a menu or run a search.
              </p>
            </div>
          ) : (
            <ul className="grid gap-4 sm:grid-cols-2">
              {items.map((item) => (
                <li key={item.food_item_id}>
                  <MenuItemCard item={item} />
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
