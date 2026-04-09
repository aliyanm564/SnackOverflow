"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import RestaurantCard from "@/components/restaurants/RestaurantCard";

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [location, setLocation] = useState("");
  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRestaurants();
  }, []);

  async function fetchRestaurants() {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ limit: "50" });
      if (query.trim()) params.set("query", query.trim());
      if (location.trim()) params.set("location", location.trim());
      const data = await apiFetch(`/api/v1/restaurants?${params}`);
      setRestaurants(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSearch(e) {
    e.preventDefault();
    fetchRestaurants();
  }

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.75rem", marginBottom: "1.25rem" }}>Browse Restaurants</h1>

      <form
        onSubmit={handleSearch}
        style={{ display: "flex", gap: "0.5rem", marginBottom: "1.75rem", flexWrap: "wrap" }}
      >
        <input
          type="text"
          placeholder="Search by name..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            flex: "2",
            minWidth: "160px",
            padding: "0.5rem 0.75rem",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        <input
          type="text"
          placeholder="Filter by location..."
          value={location}
          onChange={(e) => setLocation(e.target.value)}
          style={{
            flex: "1",
            minWidth: "130px",
            padding: "0.5rem 0.75rem",
            border: "1px solid #ccc",
            borderRadius: "4px",
          }}
        />
        <button
          type="submit"
          style={{
            padding: "0.5rem 1.1rem",
            background: "#0070f3",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          Search
        </button>
      </form>

      {loading && <p style={{ color: "#888" }}>Loading...</p>}
      {error && <p style={{ color: "#c00" }}>{error}</p>}
      {!loading && !error && restaurants.length === 0 && (
        <p style={{ color: "#888" }}>No restaurants found.</p>
      )}
      {!loading && !error && (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {restaurants.map((r) => (
            <Link
              key={r.restaurant_id}
              href={`/restaurants/${r.restaurant_id}`}
              style={{ textDecoration: "none", color: "inherit" }}
            >
              <RestaurantCard restaurant={r} />
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
