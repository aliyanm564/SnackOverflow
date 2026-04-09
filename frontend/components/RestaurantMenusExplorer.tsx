"use client";

import { fetchRestaurantMenu, getApiBase, listRestaurants, login } from "@/lib/api";
import {
  getStoredApiBase,
  getStoredToken,
  setStoredApiBase,
  setStoredToken,
} from "@/lib/storage";
import type { MenuItem, Restaurant } from "@/lib/types";
import { ChevronDown, Loader2, LogIn, MapPin, Server, Store } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { MenuItemCard } from "./MenuItemCard";
import { Section } from "./Section";

const DEFAULT_API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api/v1";

export function RestaurantMenusExplorer() {
  const [apiBase, setApiBase] = useState(DEFAULT_API_BASE);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [token, setToken] = useState("");
  const [hydrated, setHydrated] = useState(false);

  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [listError, setListError] = useState<string | null>(null);
  const [listLoading, setListLoading] = useState(false);

  const [openId, setOpenId] = useState<string | null>(null);
  const [menus, setMenus] = useState<Record<string, MenuItem[]>>({});
  const [menuErrors, setMenuErrors] = useState<Record<string, string>>({});
  const [menuLoading, setMenuLoading] = useState<string | null>(null);

  useEffect(() => {
    setApiBase(getStoredApiBase(getApiBase()));
    setToken(getStoredToken());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    setStoredApiBase(apiBase);
    setStoredToken(token);
  }, [hydrated, apiBase, token]);

  const loadRestaurants = useCallback(async () => {
    setListLoading(true);
    setListError(null);
    try {
      const rows = await listRestaurants(apiBase, 100);
      setRestaurants(rows);
    } catch (e) {
      setListError(e instanceof Error ? e.message : "Failed to load restaurants.");
      setRestaurants([]);
    } finally {
      setListLoading(false);
    }
  }, [apiBase]);

  useEffect(() => {
    if (!hydrated) return;
    void loadRestaurants();
  }, [hydrated, loadRestaurants]);

  const loadMenuForRestaurant = async (id: string, authToken?: string) => {
    const t = (authToken ?? token).trim();
    if (!t) {
      setMenuErrors((prev) => ({
        ...prev,
        [id]: "Sign in to load menu items (API requires authentication).",
      }));
      return;
    }

    setMenuLoading(id);
    setMenuErrors((prev) => {
      const next = { ...prev };
      delete next[id];
      return next;
    });
    try {
      const items = await fetchRestaurantMenu(apiBase, t, id, 100);
      setMenus((prev) => ({ ...prev, [id]: items }));
    } catch (e) {
      setMenuErrors((prev) => ({
        ...prev,
        [id]: e instanceof Error ? e.message : "Could not load menu.",
      }));
    } finally {
      setMenuLoading(null);
    }
  };

  const toggleRestaurant = async (r: Restaurant) => {
    const id = r.restaurant_id;
    if (openId === id) {
      setOpenId(null);
      return;
    }
    setOpenId(id);
    if (menus[id]) return;
    await loadMenuForRestaurant(id);
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    void (async () => {
      try {
        const data = await login(apiBase, email.trim(), password);
        const nextToken = data.access_token;
        setToken(nextToken);
        setMenuErrors({});
        setMenus({});
        if (openId && nextToken.trim()) {
          await loadMenuForRestaurant(openId, nextToken);
        }
      } catch (err) {
        alert(err instanceof Error ? err.message : "Login failed");
      }
    })();
  };

  const inputClass =
    "w-full rounded-xl border border-[var(--border)] bg-[var(--input-bg)] px-4 py-3 text-sm text-[var(--text)] placeholder:text-[var(--text-subtle)] outline-none transition focus:border-[var(--accent)] focus:ring-2 focus:ring-[var(--accent)]/25";

  const btnPrimaryClass =
    "inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent)] to-[var(--accent-strong)] px-5 py-3 text-sm font-semibold text-[var(--accent-foreground)] shadow-lg shadow-[var(--accent)]/20 transition hover:brightness-110 disabled:opacity-50";

  return (
    <div className="mx-auto max-w-3xl px-4 pb-24 pt-10 sm:px-6 lg:max-w-4xl">
      <header className="mb-10 text-center">
        <p className="mb-2 font-mono text-xs uppercase tracking-[0.2em] text-[var(--accent)]">
          SnackOverflow
        </p>
        <h1 className="font-display text-4xl font-semibold tracking-tight text-[var(--text)] sm:text-5xl">
          Restaurants and hours
        </h1>
        <p className="mx-auto mt-3 max-w-lg text-pretty text-[var(--text-muted)]">
          Pick a restaurant to open its menu. Each dish shows its{" "}
          <span className="text-[var(--text)]">available window</span> when the API provides
          times.
        </p>
      </header>

      <div className="flex flex-col gap-6">
        <Section
          title="API and sign-in"
          description="Restaurant list is public; opening menus needs a JWT."
          icon={<Server className="h-5 w-5" strokeWidth={1.75} />}
        >
          <label className="block text-sm font-medium text-[var(--text-muted)]">Base URL</label>
          <input
            className={`${inputClass} mt-2 font-mono text-xs sm:text-sm`}
            value={apiBase}
            onChange={(e) => setApiBase(e.target.value)}
            onBlur={() => void loadRestaurants()}
            placeholder="http://localhost:8000/api/v1"
            spellCheck={false}
          />
          <form onSubmit={handleLogin} className="mt-4 grid gap-3 sm:grid-cols-[1fr_1fr_auto] sm:items-end">
            <input
              className={inputClass}
              type="email"
              autoComplete="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
            <input
              className={inputClass}
              type="password"
              autoComplete="current-password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button type="submit" className={btnPrimaryClass}>
              <LogIn className="h-4 w-4" />
              Sign in
            </button>
          </form>
          <label className="mt-4 block text-sm font-medium text-[var(--text-muted)]">
            Access token
          </label>
          <textarea
            className={`${inputClass} mt-2 min-h-[72px] resize-y font-mono text-xs`}
            value={token}
            onChange={(e) => setToken(e.target.value)}
            placeholder="JWT (filled after sign-in)"
            spellCheck={false}
          />
        </Section>

        <section>
          <div className="mb-4 flex items-center justify-between gap-3">
            <h2 className="font-display text-xl font-semibold text-[var(--text)]">
              Restaurants
            </h2>
            <button
              type="button"
              onClick={() => void loadRestaurants()}
              disabled={listLoading}
              className="text-sm font-medium text-[var(--accent)] hover:underline disabled:opacity-50"
            >
              Refresh
            </button>
          </div>

          {listLoading && restaurants.length === 0 ? (
            <div className="flex items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[var(--surface)] py-14 text-[var(--text-muted)]">
              <Loader2 className="h-5 w-5 animate-spin text-[var(--accent)]" />
              Loading restaurants…
            </div>
          ) : null}

          {listError ? (
            <p className="rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {listError}
            </p>
          ) : null}

          {!listLoading && !listError && restaurants.length === 0 ? (
            <p className="text-center text-[var(--text-muted)]">No restaurants returned.</p>
          ) : null}

          <ul className="flex flex-col gap-3">
            {restaurants.map((r) => {
              const isOpen = openId === r.restaurant_id;
              const items = menus[r.restaurant_id];
              const err = menuErrors[r.restaurant_id];
              const loadingMenu = menuLoading === r.restaurant_id;

              return (
                <li
                  key={r.restaurant_id}
                  className="overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--surface)] shadow-[var(--shadow)]"
                >
                  <button
                    type="button"
                    onClick={() => void toggleRestaurant(r)}
                    className="flex w-full items-start gap-3 px-5 py-4 text-left transition hover:bg-[var(--surface-elevated)]"
                  >
                    <div className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[var(--accent-muted)] text-[var(--accent)]">
                      <Store className="h-5 w-5" strokeWidth={1.75} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="font-display text-lg font-semibold text-[var(--text)]">
                        {r.name ?? `Restaurant ${r.restaurant_id}`}
                      </p>
                      {r.location ? (
                        <p className="mt-1 flex items-center gap-1.5 text-sm text-[var(--text-muted)]">
                          <MapPin className="h-3.5 w-3.5 shrink-0" />
                          {r.location}
                        </p>
                      ) : null}
                      <p className="mt-1 font-mono text-xs text-[var(--text-subtle)]">
                        {r.restaurant_id}
                      </p>
                    </div>
                    <ChevronDown
                      className={`mt-1 h-5 w-5 shrink-0 text-[var(--text-subtle)] transition ${
                        isOpen ? "rotate-180" : ""
                      }`}
                    />
                  </button>

                  {isOpen ? (
                    <div className="border-t border-[var(--border)] bg-[var(--surface-elevated)]/60 px-5 py-5">
                      {loadingMenu ? (
                        <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                          <Loader2 className="h-4 w-4 animate-spin text-[var(--accent)]" />
                          Loading menu…
                        </div>
                      ) : err ? (
                        <p className="text-sm text-amber-200/90">{err}</p>
                      ) : items && items.length === 0 ? (
                        <p className="text-sm text-[var(--text-muted)]">No menu items.</p>
                      ) : items ? (
                        <ul className="grid gap-3 sm:grid-cols-2">
                          {items.map((item) => (
                            <li key={item.food_item_id}>
                              <MenuItemCard item={item} compact />
                            </li>
                          ))}
                        </ul>
                      ) : null}
                    </div>
                  ) : null}
                </li>
              );
            })}
          </ul>
        </section>
      </div>
    </div>
  );
}
