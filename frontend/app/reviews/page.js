"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

function StarPicker({ value, onChange }) {
  return (
    <div style={{ display: "flex", gap: "0.2rem", fontSize: "1.4rem", cursor: "pointer" }}>
      {[1, 2, 3, 4, 5].map((n) => (
        <span
          key={n}
          onClick={() => onChange(n)}
          style={{ color: n <= value ? "#f5a623" : "#ccc", userSelect: "none" }}
        >
          ★
        </span>
      ))}
    </div>
  );
}

function ReviewCard({ review, onSaved }) {
  const [editing, setEditing] = useState(false);
  const [rating, setRating] = useState(review.rating);
  const [comment, setComment] = useState(review.comment || "");
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState(null);
  const token = getToken();
  const stars = review.rating;

  async function saveEdit() {
    setSubmitting(true);
    setErr(null);
    try {
      const updated = await apiFetch(`/api/v1/reviews/${review.review_id}`, {
        method: "PATCH",
        token,
        body: JSON.stringify({ rating, comment: comment.trim() || null }),
      });
      onSaved(updated);
      setEditing(false);
    } catch (e) {
      setErr(e.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div style={{
      border: "1px solid #e0e0e0",
      borderRadius: "6px",
      padding: "1rem 1.25rem",
      background: "#fff",
    }}>
      {!editing ? (
        <>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
            <span style={{ color: "#f5a623", fontSize: "1.1rem" }}>
              {"★".repeat(stars)}{"☆".repeat(5 - stars)}
            </span>
            <span style={{ fontSize: "0.8rem", color: "#aaa" }}>
              {review.updated_at
                ? `Edited ${new Date(review.updated_at).toLocaleDateString()}`
                : new Date(review.created_at).toLocaleDateString()}
            </span>
          </div>
          {review.comment && (
            <p style={{ fontSize: "0.9rem", color: "#444", margin: "0 0 0.6rem" }}>{review.comment}</p>
          )}
          <p style={{ fontSize: "0.8rem", color: "#999", margin: "0 0 0.5rem", fontFamily: "monospace" }}>
            Order: {review.order_id.slice(0, 12)}...
          </p>
          <button
            onClick={() => { setRating(review.rating); setComment(review.comment || ""); setEditing(true); setErr(null); }}
            style={{
              fontSize: "0.8rem",
              padding: "0.25rem 0.65rem",
              border: "1px solid #ccc",
              borderRadius: "4px",
              cursor: "pointer",
              background: "#fff",
            }}
          >
            Edit
          </button>
        </>
      ) : (
        <>
          <div style={{ marginBottom: "0.5rem" }}>
            <StarPicker value={rating} onChange={setRating} />
            <p style={{ fontSize: "0.8rem", color: "#888", marginTop: "0.2rem" }}>{rating} out of 5</p>
          </div>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
            placeholder="Your comment (optional)"
            style={{
              width: "100%",
              padding: "0.4rem 0.6rem",
              border: "1px solid #ccc",
              borderRadius: "4px",
              fontSize: "0.9rem",
              resize: "vertical",
              boxSizing: "border-box",
              marginBottom: "0.5rem",
            }}
          />
          {err && <p style={{ color: "#c00", fontSize: "0.85rem", marginBottom: "0.4rem" }}>{err}</p>}
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button
              onClick={saveEdit}
              disabled={submitting}
              style={{
                padding: "0.35rem 0.85rem",
                background: "#0070f3",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: submitting ? "not-allowed" : "pointer",
                fontSize: "0.85rem",
              }}
            >
              {submitting ? "Saving..." : "Save"}
            </button>
            <button
              onClick={() => setEditing(false)}
              style={{
                padding: "0.35rem 0.75rem",
                background: "#fff",
                border: "1px solid #ccc",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "0.85rem",
              }}
            >
              Cancel
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function MyReviewsPage() {
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();
  const token = getToken();

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    apiFetch("/api/v1/reviews/my", { token })
      .then(setReviews)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  function handleSaved(updated) {
    setReviews((prev) => prev.map((r) => (r.review_id === updated.review_id ? updated : r)));
  }

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;

  return (
    <main style={{ maxWidth: "700px", margin: "0 auto", padding: "2rem 1rem" }}>
      <Link href="/orders" style={{ fontSize: "0.85rem", color: "#0070f3", textDecoration: "none" }}>
        ← My Orders
      </Link>
      <h1 style={{ fontSize: "1.6rem", margin: "1rem 0 1.5rem" }}>My Reviews</h1>

      {error && <p style={{ color: "#c00", marginBottom: "1rem" }}>{error}</p>}

      {reviews.length === 0 && !error && (
        <p style={{ color: "#888" }}>
          You haven&apos;t written any reviews yet.{" "}
          <Link href="/orders" style={{ color: "#0070f3" }}>View completed orders</Link> to leave one.
        </p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {reviews.map((r) => (
          <ReviewCard key={r.review_id} review={r} onSaved={handleSaved} />
        ))}
      </div>
    </main>
  );
}
