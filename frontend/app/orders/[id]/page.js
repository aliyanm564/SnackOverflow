"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

function formatDate(v) {
  if (!v) return "—";
  return new Date(v).toLocaleString();
}


function deriveDeliveryStatus(d) {
  if (!d) return null;
  if (d.delivery_time_actual != null) return "Delivered";
  if (d.delivery_delay != null && d.delivery_delay > 0) return "Delayed";
  if (d.delivery_time != null) return "In Transit";
  return "Pending";
}

const ORDER_BADGE = {
  pending:          { background: "#cce5ff", color: "#004085" },
  out_for_delivery: { background: "#fff3cd", color: "#856404" },
  completed:        { background: "#d4edda", color: "#155724" },
  cancelled:        { background: "#f8d7da", color: "#721c24" },
};

const DELIVERY_BADGE = {
  Delivered:    { background: "#d4edda", color: "#155724" },
  Delayed:      { background: "#fff3cd", color: "#856404" },
  "In Transit": { background: "#cce5ff", color: "#004085" },
  Pending:      { background: "#f8f9fa", color: "#6c757d" },
};

function Row({ label, value, highlight }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.9rem" }}>
      <span style={{ color: "#555" }}>{label}</span>
      <span style={{ fontWeight: 500, color: highlight ? "#856404" : "#111" }}>{value || "—"}</span>
    </div>
  );
}

function StarPicker({ value, onChange }) {
  return (
    <div style={{ display: "flex", gap: "0.25rem", fontSize: "1.5rem", cursor: "pointer" }}>
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

function ReviewSection({ orderId, token }) {
  const [existing, setExisting] = useState(null);
  const [checked, setChecked] = useState(false);
  const [editing, setEditing] = useState(false);
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitErr, setSubmitErr] = useState(null);

  useEffect(() => {
    apiFetch(`/api/v1/reviews/order/${orderId}`, { token })
      .then((r) => { setExisting(r); setChecked(true); })
      .catch((err) => {
        setChecked(true);
        if (err.status !== 404) setSubmitErr(err.message);
      });
  }, [orderId]);

  if (!checked) return null;

  async function submitReview() {
    if (!rating) return;
    setSubmitting(true);
    setSubmitErr(null);
    try {
      const r = await apiFetch("/api/v1/reviews", {
        method: "POST",
        token,
        body: JSON.stringify({ order_id: orderId, rating, comment: comment.trim() || null }),
      });
      setExisting(r);
    } catch (err) {
      setSubmitErr(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  async function saveEdit() {
    setSubmitting(true);
    setSubmitErr(null);
    try {
      const r = await apiFetch(`/api/v1/reviews/${existing.review_id}`, {
        method: "PATCH",
        token,
        body: JSON.stringify({ rating, comment: comment.trim() || null }),
      });
      setExisting(r);
      setEditing(false);
    } catch (err) {
      setSubmitErr(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  function startEdit() {
    setRating(existing.rating);
    setComment(existing.comment || "");
    setSubmitErr(null);
    setEditing(true);
  }

  const cardStyle = {
    border: "1px solid #e0e0e0",
    borderRadius: "6px",
    padding: "1rem 1.25rem",
    marginBottom: "1.25rem",
    background: "#fafafa",
  };

  if (existing && !editing) {
    const stars = existing.rating;
    return (
      <div style={cardStyle}>
        <p style={{ fontWeight: 600, fontSize: "0.875rem", marginBottom: "0.5rem" }}>Your Review</p>
        <div style={{ color: "#f5a623", fontSize: "1.2rem", marginBottom: "0.3rem" }}>
          {"★".repeat(stars)}{"☆".repeat(5 - stars)}
        </div>
        {existing.comment && (
          <p style={{ fontSize: "0.9rem", color: "#444", margin: "0 0 0.5rem" }}>{existing.comment}</p>
        )}
        <button
          onClick={startEdit}
          style={{
            fontSize: "0.85rem",
            padding: "0.3rem 0.75rem",
            border: "1px solid #ccc",
            borderRadius: "4px",
            cursor: "pointer",
            background: "#fff",
          }}
        >
          Edit Review
        </button>
      </div>
    );
  }

  return (
    <div style={cardStyle}>
      <p style={{ fontWeight: 600, fontSize: "0.875rem", marginBottom: "0.6rem" }}>
        {existing ? "Edit Your Review" : "Leave a Review"}
      </p>
      <div style={{ marginBottom: "0.6rem" }}>
        <StarPicker value={rating} onChange={setRating} />
        <p style={{ fontSize: "0.8rem", color: "#888", marginTop: "0.2rem" }}>
          {rating} out of 5
        </p>
      </div>
      <textarea
        placeholder="Share your experience (optional)"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        rows={3}
        style={{
          width: "100%",
          padding: "0.45rem 0.65rem",
          border: "1px solid #ccc",
          borderRadius: "4px",
          fontSize: "0.9rem",
          resize: "vertical",
          boxSizing: "border-box",
          marginBottom: "0.6rem",
        }}
      />
      {submitErr && (
        <p style={{ color: "#c00", fontSize: "0.85rem", marginBottom: "0.4rem" }}>{submitErr}</p>
      )}
      <div style={{ display: "flex", gap: "0.5rem" }}>
        <button
          onClick={existing ? saveEdit : submitReview}
          disabled={submitting || !rating}
          style={{
            padding: "0.45rem 1rem",
            background: "#0070f3",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: submitting ? "not-allowed" : "pointer",
            fontSize: "0.875rem",
          }}
        >
          {submitting ? "Saving..." : existing ? "Save Changes" : "Submit Review"}
        </button>
        {existing && (
          <button
            onClick={() => setEditing(false)}
            style={{
              padding: "0.45rem 0.75rem",
              background: "#fff",
              border: "1px solid #ccc",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}

export default function OrderDetailPage({ params }) {
  const { id } = params;
  const router = useRouter();
  const token = getToken();

  const [order, setOrder] = useState(null);
  const [delivery, setDelivery] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [acting, setActing] = useState(false);
  const [actionMsg, setActionMsg] = useState(null);
  const [actionErr, setActionErr] = useState(null);

  const [promoInput, setPromoInput] = useState("");
  const [promoResult, setPromoResult] = useState(null);
  const [promoError, setPromoError] = useState(null);
  const [promoLoading, setPromoLoading] = useState(false);

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    load();
  }, [id]);

  async function load() {
    const [o, d] = await Promise.allSettled([
      apiFetch(`/api/v1/orders/${id}`, { token }),
      apiFetch(`/api/v1/deliveries/${id}`),
    ]);
    if (o.status === "fulfilled") setOrder(o.value);
    else setError(o.reason.message);
    if (d.status === "fulfilled") setDelivery(d.value);
    setLoading(false);
  }

  async function applyPromo() {
    const code = promoInput.trim();
    if (!code) return;
    setPromoLoading(true);
    setPromoError(null);
    setPromoResult(null);
    try {
      const data = await apiFetch("/api/v1/promos/validate", {
        method: "POST",
        token,
        body: JSON.stringify({ code, order_id: id }),
      });
      setPromoResult(data);
    } catch (err) {
      setPromoError(err.message);
    } finally {
      setPromoLoading(false);
    }
  }

  function clearPromo() {
    setPromoInput("");
    setPromoResult(null);
    setPromoError(null);
  }

  async function pay() {
    setActing(true);
    setActionErr(null);
    setActionMsg(null);
    try {
      const body = promoResult ? { promo_code: promoInput.trim() } : undefined;
      const result = await apiFetch(`/api/v1/payments/${id}`, {
        method: "POST",
        token,
        body: body ? JSON.stringify(body) : undefined,
      });
      setActionMsg(result.message);
    } catch (err) {
      setActionErr(err.message);
    } finally {
      setActing(false);
    }
  }

  async function cancel() {
    if (!confirm("Cancel this order?")) return;
    setActing(true);
    setActionErr(null);
    try {
      const updated = await apiFetch(`/api/v1/orders/${id}/cancel`, { method: "POST", token });
      setOrder(updated);
    } catch (err) {
      setActionErr(err.message);
    } finally {
      setActing(false);
    }
  }

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;
  if (error) return (
    <main style={{ padding: "2rem" }}>
      <p style={{ color: "#c00" }}>{error}</p>
      <Link href="/orders" style={{ color: "#0070f3", fontSize: "0.9rem" }}>← Back to orders</Link>
    </main>
  );
  if (!order) return null;

  const orderBadge = ORDER_BADGE[order.status] || {};
  const deliveryStatus = deriveDeliveryStatus(delivery);
  const deliveryBadge = deliveryStatus ? DELIVERY_BADGE[deliveryStatus] || {} : {};

  return (
    <main style={{ maxWidth: "700px", margin: "0 auto", padding: "2rem 1rem" }}>
      <Link href="/orders" style={{ fontSize: "0.85rem", color: "#0070f3", textDecoration: "none" }}>
        ← My Orders
      </Link>

      <h1 style={{ fontSize: "1.5rem", margin: "1rem 0 1.5rem" }}>Order Detail</h1>

      <div style={{ border: "1px solid #e0e0e0", borderRadius: "6px", overflow: "hidden", marginBottom: "1.25rem" }}>
        <div style={{
          padding: "0.75rem 1.25rem",
          background: "#f8f8f8",
          borderBottom: "1px solid #e0e0e0",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}>
          <span style={{ fontSize: "0.85rem", color: "#666", fontFamily: "monospace" }}>{order.order_id}</span>
          <span style={{ ...orderBadge, padding: "0.15rem 0.6rem", borderRadius: "12px", fontSize: "0.8rem", fontWeight: 600 }}>
            {order.status.replace(/_/g, " ")}
          </span>
        </div>
        <div style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          <Row label="Placed" value={formatDate(order.order_time)} />
          <Row label="Items" value={`${order.items.length} item${order.items.length !== 1 ? "s" : ""}`} />
          <Row label="Order Value" value={order.order_value != null ? `$${order.order_value.toFixed(2)}` : "—"} />
        </div>
      </div>

      {delivery && (
        <div style={{ border: "1px solid #e0e0e0", borderRadius: "6px", overflow: "hidden", marginBottom: "1.25rem" }}>
          <div style={{
            padding: "0.75rem 1.25rem",
            borderBottom: "1px solid #e0e0e0",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            ...deliveryBadge,
          }}>
            <span style={{ fontWeight: 600 }}>Delivery</span>
            <span style={{ fontWeight: 600 }}>{deliveryStatus}</span>
          </div>
          <div style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.6rem" }}>
            <Row label="Method" value={delivery.delivery_method} />
            <Row label="Estimated Time" value={formatDate(delivery.delivery_time)} />
            {delivery.delivery_distance != null && (
              <Row label="Distance" value={`${delivery.delivery_distance} km`} />
            )}
          </div>
        </div>
      )}

      {!delivery && (
        <p style={{ color: "#888", fontSize: "0.9rem", marginBottom: "1.25rem" }}>
          No delivery information yet.{" "}
          <a href="/track" style={{ color: "#0070f3" }}>Track manually</a>
        </p>
      )}

      {order.status === "pending" && (
        <>
          <div style={{
            border: "1px solid #e0e0e0",
            borderRadius: "6px",
            padding: "1rem 1.25rem",
            marginBottom: "1.25rem",
            background: "#fafafa",
          }}>
            <p style={{ fontSize: "0.875rem", fontWeight: 600, marginBottom: "0.6rem" }}>Promo Code</p>
            <div style={{ display: "flex", gap: "0.5rem" }}>
              <input
                type="text"
                placeholder="Enter code"
                value={promoInput}
                onChange={(e) => { setPromoInput(e.target.value.toUpperCase()); setPromoResult(null); setPromoError(null); }}
                disabled={!!promoResult}
                style={{
                  flex: 1,
                  padding: "0.45rem 0.65rem",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                  fontSize: "0.9rem",
                  fontFamily: "monospace",
                }}
              />
              {promoResult ? (
                <button
                  onClick={clearPromo}
                  style={{ padding: "0.45rem 0.75rem", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer", background: "#fff", fontSize: "0.85rem" }}
                >
                  Remove
                </button>
              ) : (
                <button
                  onClick={applyPromo}
                  disabled={promoLoading || !promoInput.trim()}
                  style={{
                    padding: "0.45rem 0.9rem",
                    background: promoInput.trim() ? "#0070f3" : "#ccc",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    cursor: promoInput.trim() && !promoLoading ? "pointer" : "not-allowed",
                    fontSize: "0.85rem",
                  }}
                >
                  {promoLoading ? "Checking..." : "Apply"}
                </button>
              )}
            </div>

            {promoError && (
              <p style={{ color: "#c00", fontSize: "0.85rem", marginTop: "0.4rem" }}>{promoError}</p>
            )}

            {promoResult && (
              <div style={{ marginTop: "0.6rem", fontSize: "0.875rem" }}>
                <p style={{ color: "#155724", fontWeight: 600 }}>{promoResult.message}</p>
                <div style={{ display: "flex", gap: "1.5rem", marginTop: "0.3rem", color: "#444" }}>
                  <span>Discount: <strong>−${promoResult.discount_amount.toFixed(2)}</strong></span>
                  <span>Total after discount: <strong>${promoResult.adjusted_total.toFixed(2)}</strong></span>
                </div>
              </div>
            )}
          </div>

          {actionMsg && (
            <p style={{ color: "#155724", background: "#d4edda", padding: "0.5rem 1rem", borderRadius: "4px", marginBottom: "1rem" }}>
              {actionMsg}
            </p>
          )}
          {actionErr && (
            <p style={{ color: "#c00", marginBottom: "1rem" }}>{actionErr}</p>
          )}

          <div style={{ display: "flex", gap: "0.75rem" }}>
            <button
              onClick={pay}
              disabled={acting}
              style={{
                padding: "0.6rem 1.5rem",
                background: "#0070f3",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: acting ? "not-allowed" : "pointer",
              }}
            >
              {acting ? "Processing..." : promoResult ? `Pay $${promoResult.adjusted_total.toFixed(2)}` : "Pay Now"}
            </button>
            <button
              onClick={cancel}
              disabled={acting}
              style={{
                padding: "0.6rem 1.5rem",
                background: "#fff",
                color: "#c00",
                border: "1px solid #c00",
                borderRadius: "4px",
                cursor: acting ? "not-allowed" : "pointer",
              }}
            >
              Cancel Order
            </button>
          </div>
        </>
      )}

      {order.status === "completed" && (
        <>
          {actionMsg && (
            <p style={{ color: "#155724", background: "#d4edda", padding: "0.5rem 1rem", borderRadius: "4px", marginBottom: "1rem" }}>
              {actionMsg}
            </p>
          )}
          {actionErr && (
            <p style={{ color: "#c00", marginBottom: "1rem" }}>{actionErr}</p>
          )}
          <ReviewSection orderId={id} token={token} />
        </>
      )}

      {order.status === "cancelled" && (
        <>
          {actionMsg && (
            <p style={{ color: "#155724", background: "#d4edda", padding: "0.5rem 1rem", borderRadius: "4px", marginBottom: "1rem" }}>
              {actionMsg}
            </p>
          )}
          {actionErr && (
            <p style={{ color: "#c00", marginBottom: "1rem" }}>{actionErr}</p>
          )}
        </>
      )}
    </main>
  );
}
