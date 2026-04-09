"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

function isAvailableNow(from, until) {
  if (!from || !until) return true;
  const now = new Date();
  const nowMins = now.getHours() * 60 + now.getMinutes();
  const [fH, fM] = from.split(":").map(Number);
  const [uH, uM] = until.split(":").map(Number);
  const fromMins = fH * 60 + fM;
  const untilMins = uH * 60 + uM;
  if (fromMins <= untilMins) {
    return nowMins >= fromMins && nowMins <= untilMins;
  }
  return nowMins >= fromMins || nowMins <= untilMins;
}

function formatAvailability(from, until) {
  if (!from || !until) return "Always available";
  return `Available ${from.slice(0, 5)}–${until.slice(0, 5)}`;
}

function StarDisplay({ rating, count }) {
  if (rating == null) return null;
  const stars = Math.round(rating);
  return (
    <span style={{ fontSize: "0.9rem", color: "#666" }}>
      {"★".repeat(stars)}{"☆".repeat(5 - stars)}{" "}
      <strong style={{ color: "#333" }}>{rating.toFixed(1)}</strong>
      {" "}({count} {count === 1 ? "review" : "reviews"})
    </span>
  );
}

function ReviewCard({ review }) {
  const stars = review.rating;
  return (
    <div style={{
      border: "1px solid #e0e0e0",
      borderRadius: "6px",
      padding: "0.9rem 1rem",
      background: "#fff",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
        <span style={{ color: "#f5a623", fontSize: "1rem" }}>
          {"★".repeat(stars)}{"☆".repeat(5 - stars)}
        </span>
        <span style={{ fontSize: "0.8rem", color: "#aaa" }}>
          {review.created_at ? new Date(review.created_at).toLocaleDateString() : ""}
        </span>
      </div>
      {review.comment && (
        <p style={{ fontSize: "0.9rem", color: "#444", margin: 0 }}>{review.comment}</p>
      )}
    </div>
  );
}

export default function RestaurantDetailPage({ params }) {
  const { id } = params;
  const router = useRouter();
  const token = getToken();
  const user = getUser();

  const [restaurant, setRestaurant] = useState(null);
  const [menu, setMenu] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [selected, setSelected] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [ordering, setOrdering] = useState(false);
  const [orderError, setOrderError] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        const [r, rv] = await Promise.allSettled([
          apiFetch(`/api/v1/restaurants/${id}`),
          apiFetch(`/api/v1/reviews/restaurant/${id}`),
        ]);
        if (r.status === "fulfilled") setRestaurant(r.value);
        else setError(r.reason.message);
        if (rv.status === "fulfilled") setReviews(rv.value);
        if (token) {
          const m = await apiFetch(`/api/v1/restaurants/${id}/menu`, { token });
          setMenu(m);
        }
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  function toggleItem(itemId) {
    setSelected((prev) =>
      prev.includes(itemId) ? prev.filter((x) => x !== itemId) : [...prev, itemId]
    );
  }

  async function placeOrder() {
    if (!selected.length) return;
    setOrdering(true);
    setOrderError(null);
    try {
      const order = await apiFetch("/api/v1/orders", {
        method: "POST",
        token,
        body: JSON.stringify({ restaurant_id: id, food_item_ids: selected }),
      });
      router.push(`/orders/${order.order_id}`);
    } catch (err) {
      setOrderError(err.message);
      setOrdering(false);
    }
  }

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;
  if (error) return <main style={{ padding: "2rem" }}><p style={{ color: "#c00" }}>{error}</p></main>;
  if (!restaurant) return null;

  const total = selected
    .map((itemId) => menu.find((i) => i.food_item_id === itemId)?.price || 0)
    .reduce((a, b) => a + b, 0);

  const availableSelected = selected.filter((itemId) => {
    const item = menu.find((i) => i.food_item_id === itemId);
    return item ? isAvailableNow(item.available_from, item.available_until) : false;
  });

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.6rem", marginBottom: "0.25rem" }}>{restaurant.name}</h1>
      {restaurant.location && (
        <p style={{ color: "#666", fontSize: "0.9rem", marginBottom: "0.25rem" }}>{restaurant.location}</p>
      )}
      {restaurant.avg_rating != null && (
        <p style={{ marginBottom: "0.25rem" }}>
          <StarDisplay rating={restaurant.avg_rating} count={restaurant.review_count} />
        </p>
      )}
      {restaurant.avg_rating == null && (
        <p style={{ color: "#aaa", fontSize: "0.85rem", marginBottom: "0.25rem" }}>No reviews yet</p>
      )}
      {restaurant.description && (
        <p style={{ color: "#444", marginBottom: "1.5rem" }}>{restaurant.description}</p>
      )}

      <h2 style={{ fontSize: "1.2rem", marginBottom: "1rem", borderTop: "1px solid #eee", paddingTop: "1rem" }}>
        Menu
      </h2>

      {!token && (
        <p style={{ color: "#666" }}>
          <a href="/auth/login" style={{ color: "#0070f3" }}>Log in</a> to view the menu and place an order.
        </p>
      )}

      {token && menu.length === 0 && (
        <p style={{ color: "#888" }}>No menu items available.</p>
      )}

      {token && menu.length > 0 && (
        <>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem", marginBottom: "1.5rem" }}>
            {menu.map((item) => {
              const available = isAvailableNow(item.available_from, item.available_until);
              return (
                <label
                  key={item.food_item_id}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    border: `1px solid ${available ? "#e0e0e0" : "#f0c0c0"}`,
                    borderRadius: "4px",
                    padding: "0.75rem 1rem",
                    background: !available ? "#fff8f8" : selected.includes(item.food_item_id) ? "#f0f7ff" : "#fff",
                    cursor: available ? "pointer" : "not-allowed",
                    opacity: available ? 1 : 0.7,
                  }}
                >
                  <input
                    type="checkbox"
                    checked={selected.includes(item.food_item_id)}
                    onChange={() => available && toggleItem(item.food_item_id)}
                    disabled={!available}
                  />
                  <div style={{ flex: 1 }}>
                    <span style={{ fontWeight: 500, color: available ? "#111" : "#888" }}>{item.name}</span>
                    <div style={{ fontSize: "0.78rem", marginTop: "0.1rem", color: available ? "#aaa" : "#c00" }}>
                      {available
                        ? formatAvailability(item.available_from, item.available_until)
                        : `Currently unavailable · ${formatAvailability(item.available_from, item.available_until)}`}
                    </div>
                  </div>
                  {item.category && (
                    <span style={{ color: "#888", fontSize: "0.85rem" }}>{item.category}</span>
                  )}
                  {item.price != null && (
                    <span style={{ fontWeight: 600, color: available ? "#111" : "#888" }}>${item.price.toFixed(2)}</span>
                  )}
                </label>
              );
            })}
          </div>

          {selected.length > 0 && (
            <p style={{ marginBottom: "0.75rem", fontSize: "0.95rem", color: "#333" }}>
              {availableSelected.length} of {selected.length} selected item{selected.length !== 1 ? "s" : ""} available
              {total > 0 && ` · $${total.toFixed(2)}`}
            </p>
          )}

          {orderError && (
            <p style={{ color: "#c00", marginBottom: "0.75rem" }}>{orderError}</p>
          )}

          {user?.role === "customer" && (
            <button
              onClick={placeOrder}
              disabled={!availableSelected.length || ordering}
              style={{
                padding: "0.6rem 1.5rem",
                background: availableSelected.length ? "#0070f3" : "#ccc",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: availableSelected.length && !ordering ? "pointer" : "not-allowed",
              }}
            >
              {ordering ? "Placing order..." : "Place Order"}
            </button>
          )}
        </>
      )}

      <h2 style={{
        fontSize: "1.2rem",
        margin: "2rem 0 1rem",
        borderTop: "1px solid #eee",
        paddingTop: "1rem",
      }}>
        Reviews {reviews.length > 0 && `(${reviews.length})`}
      </h2>

      {reviews.length === 0 && (
        <p style={{ color: "#888", fontSize: "0.9rem" }}>No reviews yet for this restaurant.</p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {reviews.map((rv) => (
          <ReviewCard key={rv.review_id} review={rv} />
        ))}
      </div>
    </main>
  );
}
