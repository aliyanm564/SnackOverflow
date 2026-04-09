"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

const DELIVERY_METHODS = ["walk", "bike", "car", "mixed"];

const STATUS_BADGE = {
  pending:          { background: "#cce5ff", color: "#004085" },
  out_for_delivery: { background: "#fff3cd", color: "#856404" },
  completed:        { background: "#d4edda", color: "#155724" },
  cancelled:        { background: "#f8d7da", color: "#721c24" },
};

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

function formatItems(items) {
  if (!items?.length) return "—";
  return `${items.length} item${items.length !== 1 ? "s" : ""}`;
}

export default function AdminOrdersPage() {
  const router = useRouter();
  const token = getToken();
  const user = getUser();

  const [restaurants, setRestaurants] = useState([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState(null);
  const [orders, setOrders] = useState([]);
  const [loadingRestaurants, setLoadingRestaurants] = useState(true);
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [error, setError] = useState(null);

  // completing state
  const [completing, setCompleting] = useState(null);

  // delivery assignment state per order
  const [assigningOrderId, setAssigningOrderId] = useState(null);
  const [deliveryForm, setDeliveryForm] = useState({
    delivery_method: "bike",
    delivery_distance: "",
    estimated_delivery_time: "",
  });
  const [assignError, setAssignError] = useState(null);
  const [assigning, setAssigning] = useState(false);

  useEffect(() => {
    if (!token || user?.role !== "restaurant_owner") {
      router.push("/auth/login");
      return;
    }
    fetchRestaurants();
  }, []);

  async function fetchRestaurants() {
    try {
      const data = await apiFetch(`/api/v1/restaurants/owner/${user.customer_id}`, { token });
      setRestaurants(data);
      if (data.length > 0) {
        setSelectedRestaurant(data[0]);
        fetchOrders(data[0].restaurant_id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingRestaurants(false);
    }
  }

  async function fetchOrders(restaurantId) {
    setLoadingOrders(true);
    setError(null);
    try {
      const data = await apiFetch(`/api/v1/orders/restaurant/${restaurantId}`, { token });
      // newest first
      setOrders([...data].sort((a, b) => new Date(b.order_time) - new Date(a.order_time)));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingOrders(false);
    }
  }

  function selectRestaurant(r) {
    setSelectedRestaurant(r);
    setOrders([]);
    setAssigningOrderId(null);
    fetchOrders(r.restaurant_id);
  }

  async function completeOrder(orderId) {
    setCompleting(orderId);
    try {
      await apiFetch(`/api/v1/orders/${orderId}/complete`, { method: "POST", token });
      setOrders((prev) =>
        prev.map((o) => (o.order_id === orderId ? { ...o, status: "completed" } : o))
      );
    } catch (err) {
      alert(`Failed to mark as delivered: ${err.message}`);
    } finally {
      setCompleting(null);
    }
  }

  function startAssign(orderId) {
    setAssigningOrderId(orderId);
    setDeliveryForm({ delivery_method: "bike", delivery_distance: "", estimated_delivery_time: "" });
    setAssignError(null);
  }

  async function submitAssign(e) {
    e.preventDefault();
    setAssigning(true);
    setAssignError(null);

    const body = {
      delivery_method: deliveryForm.delivery_method || undefined,
    };
    if (deliveryForm.delivery_distance !== "") {
      body.delivery_distance = parseFloat(deliveryForm.delivery_distance);
    }
    if (deliveryForm.estimated_delivery_time !== "") {
      body.estimated_delivery_time = new Date(deliveryForm.estimated_delivery_time).toISOString();
    }

    try {
      await apiFetch(`/api/v1/deliveries/${assigningOrderId}`, {
        method: "POST",
        token,
        body: JSON.stringify(body),
      });
      // update the order in local state to out_for_delivery
      setOrders((prev) =>
        prev.map((o) =>
          o.order_id === assigningOrderId ? { ...o, status: "out_for_delivery" } : o
        )
      );
      setAssigningOrderId(null);
    } catch (err) {
      setAssignError(err.message);
    } finally {
      setAssigning(false);
    }
  }

  if (loadingRestaurants) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;

  return (
    <main style={{ maxWidth: "900px", margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.6rem" }}>Incoming Orders</h1>
        <button
          onClick={() => router.push("/admin")}
          style={{ fontSize: "0.875rem", padding: "0.4rem 0.85rem", background: "#f5f5f5", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer" }}
        >
          ← Back to Admin
        </button>
      </div>

      {/* Restaurant selector */}
      {restaurants.length > 1 && (
        <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
          {restaurants.map((r) => (
            <button
              key={r.restaurant_id}
              onClick={() => selectRestaurant(r)}
              style={{
                padding: "0.4rem 0.9rem",
                borderRadius: "20px",
                border: "1px solid",
                fontSize: "0.875rem",
                cursor: "pointer",
                borderColor: selectedRestaurant?.restaurant_id === r.restaurant_id ? "#0070f3" : "#ccc",
                background: selectedRestaurant?.restaurant_id === r.restaurant_id ? "#e8f0fe" : "#fff",
                color: selectedRestaurant?.restaurant_id === r.restaurant_id ? "#0070f3" : "#333",
                fontWeight: selectedRestaurant?.restaurant_id === r.restaurant_id ? 600 : 400,
              }}
            >
              {r.name}
            </button>
          ))}
        </div>
      )}

      {restaurants.length === 0 && (
        <p style={{ color: "#888" }}>No restaurants found. <a href="/admin" style={{ color: "#0070f3" }}>Create one first.</a></p>
      )}

      {error && <p style={{ color: "#c00", marginBottom: "1rem" }}>{error}</p>}

      {loadingOrders && <p style={{ color: "#888" }}>Loading orders...</p>}

      {!loadingOrders && selectedRestaurant && orders.length === 0 && !error && (
        <div style={{ textAlign: "center", padding: "3rem 1rem", color: "#888" }}>
          <p style={{ fontSize: "1.1rem", marginBottom: "0.5rem" }}>No orders yet</p>
          <p style={{ fontSize: "0.9rem" }}>Orders for {selectedRestaurant.name} will appear here.</p>
        </div>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {orders.map((order) => {
          const badge = STATUS_BADGE[order.status] || {};
          const isPending = order.status === "pending";
          const isAssigningThis = assigningOrderId === order.order_id;

          return (
            <div
              key={order.order_id}
              style={{
                border: "1px solid",
                borderColor: isPending ? "#b3d4fb" : "#e0e0e0",
                borderRadius: "6px",
                background: "#fff",
                overflow: "hidden",
              }}
            >
              {/* Order header */}
              <div style={{
                padding: "0.75rem 1.25rem",
                background: isPending ? "#f0f7ff" : "#fafafa",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                borderBottom: "1px solid #e0e0e0",
              }}>
                <span style={{ fontFamily: "monospace", fontSize: "0.85rem", color: "#555" }}>
                  {order.order_id}
                </span>
                <span style={{
                  ...badge,
                  padding: "0.2rem 0.65rem",
                  borderRadius: "12px",
                  fontSize: "0.8rem",
                  fontWeight: 600,
                }}>
                  {order.status.replace(/_/g, " ")}
                </span>
              </div>

              {/* Order body */}
              <div style={{ padding: "1rem 1.25rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
                  <div>
                    <p style={{ margin: "0 0 0.2rem", fontWeight: 600, fontSize: "0.95rem" }}>
                      {formatItems(order.items)}
                      {order.order_value != null && (
                        <span style={{ fontWeight: 400, color: "#555", marginLeft: "0.5rem" }}>
                          · ${order.order_value.toFixed(2)}
                        </span>
                      )}
                    </p>
                    <p style={{ margin: 0, fontSize: "0.85rem", color: "#888" }}>
                      Placed {formatDate(order.order_time)}
                    </p>
                  </div>

                  {isPending && !isAssigningThis && (
                    <button
                      onClick={() => startAssign(order.order_id)}
                      style={{
                        padding: "0.45rem 1rem",
                        background: "#0070f3",
                        color: "#fff",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "0.875rem",
                        fontWeight: 600,
                      }}
                    >
                      Assign Delivery
                    </button>
                  )}

                  {order.status === "out_for_delivery" && (
                    <button
                      onClick={() => completeOrder(order.order_id)}
                      disabled={completing === order.order_id}
                      style={{
                        padding: "0.45rem 1rem",
                        background: completing === order.order_id ? "#999" : "#198754",
                        color: "#fff",
                        border: "none",
                        borderRadius: "4px",
                        cursor: completing === order.order_id ? "not-allowed" : "pointer",
                        fontSize: "0.875rem",
                        fontWeight: 600,
                      }}
                    >
                      {completing === order.order_id ? "Saving..." : "Mark as Delivered"}
                    </button>
                  )}
                </div>

                {/* Delivery assignment form */}
                {isAssigningThis && (
                  <form
                    onSubmit={submitAssign}
                    style={{
                      marginTop: "1rem",
                      paddingTop: "1rem",
                      borderTop: "1px solid #e0e0e0",
                      display: "flex",
                      flexDirection: "column",
                      gap: "0.65rem",
                    }}
                  >
                    <h3 style={{ margin: 0, fontSize: "0.95rem", color: "#333" }}>Assign Delivery</h3>

                    <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                      <div style={{ flex: "1 1 160px" }}>
                        <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.3rem" }}>
                          Delivery Method
                        </label>
                        <select
                          value={deliveryForm.delivery_method}
                          onChange={(e) => setDeliveryForm((p) => ({ ...p, delivery_method: e.target.value }))}
                          style={{ width: "100%", padding: "0.45rem 0.6rem", border: "1px solid #ccc", borderRadius: "4px", fontSize: "0.9rem" }}
                        >
                          {DELIVERY_METHODS.map((m) => (
                            <option key={m} value={m}>{m.charAt(0).toUpperCase() + m.slice(1)}</option>
                          ))}
                        </select>
                      </div>

                      <div style={{ flex: "1 1 160px" }}>
                        <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.3rem" }}>
                          Distance (km)
                        </label>
                        <input
                          type="number"
                          min="0"
                          step="0.1"
                          placeholder="e.g. 3.5"
                          value={deliveryForm.delivery_distance}
                          onChange={(e) => setDeliveryForm((p) => ({ ...p, delivery_distance: e.target.value }))}
                          style={{ width: "100%", padding: "0.45rem 0.6rem", border: "1px solid #ccc", borderRadius: "4px", fontSize: "0.9rem", boxSizing: "border-box" }}
                        />
                      </div>

                      <div style={{ flex: "1 1 200px" }}>
                        <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.3rem" }}>
                          Estimated Delivery Time
                        </label>
                        <input
                          type="datetime-local"
                          value={deliveryForm.estimated_delivery_time}
                          onChange={(e) => setDeliveryForm((p) => ({ ...p, estimated_delivery_time: e.target.value }))}
                          style={{ width: "100%", padding: "0.45rem 0.6rem", border: "1px solid #ccc", borderRadius: "4px", fontSize: "0.9rem", boxSizing: "border-box" }}
                        />
                      </div>
                    </div>

                    {assignError && (
                      <p style={{ color: "#c00", fontSize: "0.875rem", margin: 0 }}>{assignError}</p>
                    )}

                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button
                        type="submit"
                        disabled={assigning}
                        style={{
                          padding: "0.45rem 1rem",
                          background: assigning ? "#999" : "#0070f3",
                          color: "#fff",
                          border: "none",
                          borderRadius: "4px",
                          cursor: assigning ? "not-allowed" : "pointer",
                          fontSize: "0.875rem",
                          fontWeight: 600,
                        }}
                      >
                        {assigning ? "Assigning..." : "Confirm"}
                      </button>
                      <button
                        type="button"
                        onClick={() => setAssigningOrderId(null)}
                        style={{
                          padding: "0.45rem 1rem",
                          background: "#fff",
                          border: "1px solid #ccc",
                          borderRadius: "4px",
                          cursor: "pointer",
                          fontSize: "0.875rem",
                        }}
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </main>
  );
}
