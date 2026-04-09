"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

const STATUS_CONFIG = {
  pending:          { label: "Pending",          background: "#e9ecef", color: "#495057" },
  out_for_delivery: { label: "Out for Delivery",  background: "#fff3cd", color: "#856404" },
  completed:        { label: "Delivered",          background: "#d4edda", color: "#155724" },
  cancelled:        { label: "Cancelled",          background: "#f8d7da", color: "#721c24" },
};

function formatDateTime(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export default function TrackPage() {
  const router = useRouter();
  const token = getToken();

  const [orderId, setOrderId] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  async function fetchTracking() {
    const id = orderId.trim();
    if (!id) return;

    if (!token) {
      router.push("/auth/login");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await apiFetch(`/api/v1/orders/${encodeURIComponent(id)}/track`, { token });
      setResult(data);
    } catch (err) {
      if (err.status === 403) {
        setError("This order does not belong to your account.");
      } else if (err.status === 404) {
        setError("Order not found. Please check the ID and try again.");
      } else {
        setError(err.message);
      }
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter") fetchTracking();
  }

  const statusConfig = result ? (STATUS_CONFIG[result.status] || { label: result.status, background: "#e9ecef", color: "#333" }) : null;
  const deliveryAssigned = result && (result.delivery_method || result.estimated_delivery_time || result.delivery_distance);

  return (
    <main style={{ maxWidth: "640px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.6rem", marginBottom: "0.25rem" }}>Track Order</h1>
      <p style={{ color: "#666", marginBottom: "1.75rem", fontSize: "0.9rem" }}>
        Enter your order ID to see its current status and delivery info.
      </p>

      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem" }}>
        <input
          type="text"
          placeholder="Order ID"
          value={orderId}
          onChange={(e) => setOrderId(e.target.value)}
          onKeyDown={handleKeyDown}
          style={{
            flex: 1,
            padding: "0.55rem 0.75rem",
            border: "1px solid #ccc",
            borderRadius: "4px",
            fontSize: "0.95rem",
          }}
        />
        <button
          onClick={fetchTracking}
          disabled={loading || !orderId.trim()}
          style={{
            padding: "0.55rem 1.1rem",
            background: loading ? "#999" : "#0070f3",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: loading || !orderId.trim() ? "not-allowed" : "pointer",
            fontSize: "0.95rem",
          }}
        >
          {loading ? "Loading…" : result ? "Refresh" : "Track"}
        </button>
      </div>

      {error && (
        <p style={{ color: "#c00", marginBottom: "1rem", fontSize: "0.9rem" }}>{error}</p>
      )}

      {result && (
        <div style={{ border: "1px solid #e0e0e0", borderRadius: "6px", overflow: "hidden" }}>
          {/* Status banner */}
          <div style={{
            padding: "1rem 1.25rem",
            background: statusConfig.background,
            color: statusConfig.color,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}>
            <span style={{ fontWeight: 700, fontSize: "1.05rem" }}>{statusConfig.label}</span>
            <span style={{ fontSize: "0.8rem", opacity: 0.8 }}>
              {result.order_time ? new Date(result.order_time).toLocaleDateString() : ""}
            </span>
          </div>

          {/* Order details */}
          <div style={{ padding: "1.25rem", display: "flex", flexDirection: "column", gap: "0.7rem" }}>
            <Row label="Order ID" value={<span style={{ fontFamily: "monospace", fontSize: "0.85rem" }}>{result.order_id}</span>} />
            <Row label="Items" value={`${result.items?.length ?? 0} item${result.items?.length !== 1 ? "s" : ""}`} />
            {result.order_value != null && (
              <Row label="Order Total" value={`$${result.order_value.toFixed(2)}`} />
            )}

            {/* Divider before delivery section */}
            <div style={{ borderTop: "1px solid #f0f0f0", paddingTop: "0.7rem", marginTop: "0.2rem" }}>
              <p style={{ margin: "0 0 0.6rem", fontSize: "0.8rem", fontWeight: 600, color: "#888", textTransform: "uppercase", letterSpacing: "0.05em" }}>
                Delivery
              </p>

              {deliveryAssigned ? (
                <>
                  {result.delivery_method && (
                    <Row label="Method" value={result.delivery_method.charAt(0).toUpperCase() + result.delivery_method.slice(1)} />
                  )}
                  {result.delivery_distance != null && (
                    <Row label="Distance" value={`${result.delivery_distance} km`} />
                  )}
                  {result.estimated_delivery_time && (
                    <Row label="Estimated Arrival" value={formatDateTime(result.estimated_delivery_time)} highlight />
                  )}
                </>
              ) : (
                <p style={{ fontSize: "0.9rem", color: "#888", margin: 0 }}>
                  {result.status === "pending"
                    ? "Waiting for the restaurant to assign a delivery driver."
                    : "No delivery details available."}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

function Row({ label, value, highlight }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: "0.9rem" }}>
      <span style={{ color: "#555" }}>{label}</span>
      <span style={{ fontWeight: 500, color: highlight ? "#856404" : "#111" }}>{value || "—"}</span>
    </div>
  );
}
