"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

function StarDisplay({ rating }) {
  const stars = Math.round(rating);
  return (
    <span style={{ color: "#f5a623", fontSize: "1rem" }}>
      {"★".repeat(stars)}{"☆".repeat(5 - stars)}
    </span>
  );
}

export default function AdminReviewsPage() {
  const router = useRouter();
  const token = getToken();
  const user = getUser();

  const [restaurants, setRestaurants] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [reviews, setReviews] = useState([]);
  const [loadingRestaurants, setLoadingRestaurants] = useState(true);
  const [loadingReviews, setLoadingReviews] = useState(false);
  const [error, setError] = useState(null);
  const [reviewError, setReviewError] = useState(null);

  useEffect(() => {
    if (!token || user?.role !== "restaurant_owner") {
      router.push("/auth/login");
      return;
    }
    apiFetch(`/api/v1/restaurants/owner/${user.customer_id}`, { token })
      .then((data) => {
        setRestaurants(data);
        if (data.length > 0) setSelectedId(data[0].restaurant_id);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoadingRestaurants(false));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoadingReviews(true);
    setReviewError(null);
    apiFetch(`/api/v1/reviews/restaurant/${selectedId}`, { token })
      .then(setReviews)
      .catch((e) => setReviewError(e.message))
      .finally(() => setLoadingReviews(false));
  }, [selectedId]);

  const selectedRestaurant = restaurants.find((r) => r.restaurant_id === selectedId);

  if (loadingRestaurants) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <Link href="/admin" style={{ fontSize: "0.85rem", color: "#0070f3", textDecoration: "none" }}>
        ← Admin Dashboard
      </Link>
      <h1 style={{ fontSize: "1.6rem", margin: "1rem 0 1.5rem" }}>Restaurant Reviews</h1>

      {error && <p style={{ color: "#c00", marginBottom: "1rem" }}>{error}</p>}

      {restaurants.length === 0 && !error && (
        <p style={{ color: "#888" }}>
          No restaurants found.{" "}
          <Link href="/admin" style={{ color: "#0070f3" }}>Create one first.</Link>
        </p>
      )}

      {restaurants.length > 0 && (
        <>
          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.4rem", color: "#333" }}>
              Select Restaurant
            </label>
            <select
              value={selectedId}
              onChange={(e) => setSelectedId(e.target.value)}
              style={{
                padding: "0.45rem 0.65rem",
                border: "1px solid #ccc",
                borderRadius: "4px",
                fontSize: "0.9rem",
                minWidth: "240px",
              }}
            >
              {restaurants.map((r) => (
                <option key={r.restaurant_id} value={r.restaurant_id}>
                  {r.name || "Unnamed"}
                </option>
              ))}
            </select>
          </div>

          {selectedRestaurant && (
            <div style={{
              border: "1px solid #e0e0e0",
              borderRadius: "6px",
              padding: "0.9rem 1.25rem",
              background: "#f8f8f8",
              marginBottom: "1.25rem",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}>
              <div>
                <p style={{ fontWeight: 600, margin: "0 0 0.15rem", fontSize: "1rem" }}>{selectedRestaurant.name}</p>
                {selectedRestaurant.location && (
                  <p style={{ color: "#666", fontSize: "0.85rem", margin: 0 }}>{selectedRestaurant.location}</p>
                )}
              </div>
              <div style={{ textAlign: "right" }}>
                {selectedRestaurant.avg_rating != null ? (
                  <>
                    <StarDisplay rating={selectedRestaurant.avg_rating} />
                    <p style={{ fontSize: "0.85rem", color: "#555", margin: "0.2rem 0 0" }}>
                      {selectedRestaurant.avg_rating.toFixed(1)} avg · {selectedRestaurant.review_count} {selectedRestaurant.review_count === 1 ? "review" : "reviews"}
                    </p>
                  </>
                ) : (
                  <p style={{ color: "#aaa", fontSize: "0.85rem", margin: 0 }}>No reviews yet</p>
                )}
              </div>
            </div>
          )}

          {loadingReviews && <p style={{ color: "#888" }}>Loading reviews...</p>}
          {reviewError && <p style={{ color: "#c00" }}>{reviewError}</p>}

          {!loadingReviews && !reviewError && reviews.length === 0 && (
            <p style={{ color: "#888", fontSize: "0.9rem" }}>No reviews for this restaurant yet.</p>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {reviews.map((rv) => {
              const stars = rv.rating;
              return (
                <div
                  key={rv.review_id}
                  style={{
                    border: "1px solid #e0e0e0",
                    borderRadius: "6px",
                    padding: "0.9rem 1.25rem",
                    background: "#fff",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.3rem" }}>
                    <span style={{ color: "#f5a623", fontSize: "1rem" }}>
                      {"★".repeat(stars)}{"☆".repeat(5 - stars)}
                      <span style={{ color: "#555", fontSize: "0.85rem", marginLeft: "0.4rem" }}>
                        {rv.rating}/5
                      </span>
                    </span>
                    <span style={{ fontSize: "0.8rem", color: "#aaa" }}>
                      {rv.updated_at
                        ? `Edited ${new Date(rv.updated_at).toLocaleDateString()}`
                        : new Date(rv.created_at).toLocaleDateString()}
                    </span>
                  </div>
                  {rv.comment && (
                    <p style={{ fontSize: "0.9rem", color: "#444", margin: "0 0 0.4rem" }}>{rv.comment}</p>
                  )}
                  <p style={{ fontSize: "0.78rem", color: "#bbb", margin: 0, fontFamily: "monospace" }}>
                    Order: {rv.order_id.slice(0, 16)}...
                  </p>
                </div>
              );
            })}
          </div>
        </>
      )}
    </main>
  );
}
