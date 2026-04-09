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

  const [editingOrder, setEditingOrder] = useState(null);
  const [menuItems, setMenuItems] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);
  const [menuLoading, setMenuLoading] = useState(false);
  const [menuError, setMenuError] = useState(null);
  const [placing, setPlacing] = useState(false);
  const [placeError, setPlaceError] = useState(null);

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

  async function openReorderEdit(order) {
    setEditingOrder(order);
    setSelectedIds([...order.items]);
    setMenuError(null);
    setPlaceError(null);
    setMenuLoading(true);
    try {
      const items = await apiFetch(
        `/api/v1/restaurants/${order.restaurant_id}/menu?limit=100`,
        { token }
      );
      setMenuItems(items);
    } catch (err) {
      setMenuError("Could not load menu.");
    } finally {
      setMenuLoading(false);
    }
  }

  function toggleItem(id) {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function confirmReorder() {
    if (!editingOrder || selectedIds.length === 0) return;
    setPlacing(true);
    setPlaceError(null);
    try {
      const newOrder = await apiFetch(
        `/api/v1/orders/${editingOrder.order_id}/reorder`,
        {
          method: "POST",
          token,
          body: JSON.stringify({ food_item_ids: selectedIds }),
        }
      );
      router.push(`/orders/${newOrder.order_id}`);
    } catch (err) {
      setPlaceError(err.message);
      setPlacing(false);
    }
  }

  function closeEdit() {
    setEditingOrder(null);
    setMenuItems([]);
    setSelectedIds([]);
    setMenuError(null);
    setPlaceError(null);
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
          const isEditing = editingOrder?.order_id === order.order_id;

          return (
            <div
              key={order.order_id}
              style={{
                border: `1px solid ${isEditing ? "#0070f3" : "#e0e0e0"}`,
                borderRadius: "6px",
                background: "#fff",
                overflow: "hidden",
              }}
            >
              <div style={{ padding: "1rem 1.25rem" }}>
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

                  {(order.status === "completed" || order.status === "cancelled") && (
                    <>
                      <button
                        onClick={() => isEditing ? closeEdit() : openReorderEdit(order)}
                        style={{
                          fontSize: "0.85rem",
                          padding: "0.3rem 0.75rem",
                          background: isEditing ? "#fff" : "#0070f3",
                          color: isEditing ? "#333" : "#fff",
                          border: isEditing ? "1px solid #ccc" : "none",
                          borderRadius: "4px",
                          cursor: "pointer",
                        }}
                      >
                        {isEditing ? "Cancel" : "Reorder"}
                      </button>
                      {order.status === "completed" && (
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
                      )}
                    </>
                  )}
                </div>
              </div>

              {isEditing && (
                <div style={{
                  borderTop: "1px solid #e0e0e0",
                  padding: "1rem 1.25rem",
                  background: "#f9fbff",
                }}>
                  <p style={{ fontWeight: 600, fontSize: "0.875rem", marginBottom: "0.75rem" }}>
                    Edit your reorder
                  </p>

                  {menuLoading && <p style={{ fontSize: "0.9rem", color: "#888" }}>Loading menu...</p>}
                  {menuError && <p style={{ fontSize: "0.9rem", color: "#c00" }}>{menuError}</p>}

                  {!menuLoading && !menuError && (
                    <>
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem", marginBottom: "0.75rem", maxHeight: "220px", overflowY: "auto" }}>
                        {menuItems.map((item) => {
                          const checked = selectedIds.includes(item.food_item_id);
                          return (
                            <label
                              key={item.food_item_id}
                              style={{
                                display: "flex",
                                alignItems: "center",
                                gap: "0.6rem",
                                fontSize: "0.9rem",
                                cursor: "pointer",
                                padding: "0.35rem 0.5rem",
                                borderRadius: "4px",
                                background: checked ? "#e8f0fe" : "transparent",
                              }}
                            >
                              <input
                                type="checkbox"
                                checked={checked}
                                onChange={() => toggleItem(item.food_item_id)}
                              />
                              <span style={{ flex: 1 }}>{item.name}</span>
                              {item.price != null && (
                                <span style={{ color: "#555", fontWeight: 500 }}>${item.price.toFixed(2)}</span>
                              )}
                            </label>
                          );
                        })}
                      </div>

                      {placeError && (
                        <p style={{ color: "#c00", fontSize: "0.85rem", marginBottom: "0.5rem" }}>{placeError}</p>
                      )}

                      <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                        <button
                          onClick={confirmReorder}
                          disabled={placing || selectedIds.length === 0}
                          style={{
                            padding: "0.45rem 1.1rem",
                            background: selectedIds.length === 0 ? "#ccc" : "#0070f3",
                            color: "#fff",
                            border: "none",
                            borderRadius: "4px",
                            cursor: placing || selectedIds.length === 0 ? "not-allowed" : "pointer",
                            fontSize: "0.875rem",
                          }}
                        >
                          {placing ? "Placing..." : `Confirm Reorder (${selectedIds.length} item${selectedIds.length !== 1 ? "s" : ""})`}
                        </button>
                        <span style={{ fontSize: "0.8rem", color: "#888" }}>
                          {selectedIds.length === 0 && "Select at least one item"}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </main>
  );
}
