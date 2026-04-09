"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

const STATUS_BADGE = {
  pending:          { background: "#cce5ff", color: "#004085" },
  out_for_delivery: { background: "#fff3cd", color: "#856404" },
  completed:        { background: "#d4edda", color: "#155724" },
  cancelled:        { background: "#f8d7da", color: "#721c24" },
};

export default function OrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [reordering, setReordering] = useState(null);
  const router = useRouter();
  const token = getToken();

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    fetchOrders();
  }, []);

  async function fetchOrders() {
    try {
      const data = await apiFetch("/api/v1/orders?limit=50", { token });
      setOrders(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function reorder(order) {
    setReordering(order.order_id);
    try {
      const newOrder = await apiFetch("/api/v1/orders", {
        method: "POST",
        token,
        body: JSON.stringify({
          restaurant_id: order.restaurant_id,
          food_item_ids: order.items,
        }),
      });
      router.push(`/orders/${newOrder.order_id}`);
    } catch (err) {
      alert(`Reorder failed: ${err.message}`);
      setReordering(null);
    }
  }

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;
  if (error) return <main style={{ padding: "2rem" }}><p style={{ color: "#c00" }}>{error}</p></main>;

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.6rem" }}>My Orders</h1>
        <Link
          href="/reviews"
          style={{
            fontSize: "0.875rem",
            padding: "0.4rem 0.85rem",
            background: "#f0f7ff",
            color: "#0070f3",
            border: "1px solid #b3d4fb",
            borderRadius: "4px",
            textDecoration: "none",
          }}
        >
          My Reviews
        </Link>
      </div>

      {orders.length === 0 && (
        <p style={{ color: "#888" }}>
          No orders yet.{" "}
          <Link href="/" style={{ color: "#0070f3" }}>Browse restaurants</Link>
        </p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {orders.map((order) => {
          const badge = STATUS_BADGE[order.status] || {};
          return (
            <div
              key={order.order_id}
              style={{
                border: "1px solid #e0e0e0",
                borderRadius: "6px",
                padding: "1rem 1.25rem",
                background: "#fff",
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "0.85rem", color: "#888", fontFamily: "monospace" }}>
                  {order.order_id.slice(0, 12)}...
                </span>
                <span style={{
                  ...badge,
                  padding: "0.15rem 0.6rem",
                  borderRadius: "12px",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                }}>
                  {order.status.replace(/_/g, " ")}
                </span>
              </div>

              <p style={{ fontSize: "0.9rem", color: "#333", marginBottom: "0.2rem" }}>
                {order.items.length} item{order.items.length !== 1 ? "s" : ""}
                {order.order_value != null && ` · $${order.order_value.toFixed(2)}`}
              </p>
              <p style={{ fontSize: "0.85rem", color: "#888", marginBottom: "0.75rem" }}>
                {formatDate(order.order_time)}
              </p>

              <div style={{ display: "flex", gap: "0.5rem" }}>
                <Link
                  href={`/orders/${order.order_id}`}
                  style={{
                    fontSize: "0.85rem",
                    padding: "0.3rem 0.75rem",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    textDecoration: "none",
                    color: "#333",
                  }}
                >
                  View
                </Link>

                {order.status === "completed" && (
                  <>
                    <button
                      onClick={() => reorder(order)}
                      disabled={reordering === order.order_id}
                      style={{
                        fontSize: "0.85rem",
                        padding: "0.3rem 0.75rem",
                        background: "#0070f3",
                        color: "#fff",
                        border: "none",
                        borderRadius: "4px",
                        cursor: reordering === order.order_id ? "not-allowed" : "pointer",
                      }}
                    >
                      {reordering === order.order_id ? "Placing..." : "Reorder"}
                    </button>
                    <Link
                      href={`/orders/${order.order_id}`}
                      style={{
                        fontSize: "0.85rem",
                        padding: "0.3rem 0.75rem",
                        background: "#fff8e1",
                        color: "#856404",
                        border: "1px solid #ffc107",
                        borderRadius: "4px",
                        textDecoration: "none",
                      }}
                    >
                      Review
                    </Link>
                  </>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}
