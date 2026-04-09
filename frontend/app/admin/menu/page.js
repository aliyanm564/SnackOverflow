"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

const inputStyle = {
  padding: "0.4rem 0.6rem",
  border: "1px solid #ccc",
  borderRadius: "4px",
  fontSize: "0.9rem",
};

function toTimeInput(apiTime) {
  if (!apiTime) return "";
  return apiTime.slice(0, 5);
}

function toApiTime(inputVal) {
  if (!inputVal) return null;
  return inputVal.length === 5 ? `${inputVal}:00` : inputVal;
}

function availabilityText(from, until) {
  if (!from || !until) return "Always available";
  return `${toTimeInput(from)} – ${toTimeInput(until)}`;
}

function MenuManager() {
  const searchParams = useSearchParams();
  const restaurantId = searchParams.get("restaurant");
  const router = useRouter();
  const token = getToken();
  const user = getUser();

  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [adding, setAdding] = useState(false);
  const [newItem, setNewItem] = useState({
    name: "", category: "", price: "", available_from: "", available_until: "",
  });
  const [addError, setAddError] = useState(null);

  const [editingId, setEditingId] = useState(null);
  const [editItem, setEditItem] = useState({});
  const [editError, setEditError] = useState(null);

  useEffect(() => {
    if (!token || user?.role !== "restaurant_owner") { router.push("/auth/login"); return; }
    if (!restaurantId) { router.push("/admin"); return; }
    fetchMenu();
  }, [restaurantId]);

  async function fetchMenu() {
    setLoading(true);
    try {
      const data = await apiFetch(`/api/v1/restaurants/${restaurantId}/menu`, { token });
      setItems(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function addItem(e) {
    e.preventDefault();
    setAddError(null);
    try {
      const item = await apiFetch(`/api/v1/restaurants/${restaurantId}/menu`, {
        method: "POST",
        token,
        body: JSON.stringify({
          name: newItem.name,
          category: newItem.category || undefined,
          price: newItem.price !== "" ? parseFloat(newItem.price) : undefined,
          available_from: toApiTime(newItem.available_from),
          available_until: toApiTime(newItem.available_until),
        }),
      });
      setItems((prev) => [...prev, item]);
      setNewItem({ name: "", category: "", price: "", available_from: "", available_until: "" });
      setAdding(false);
    } catch (err) {
      setAddError(err.message);
    }
  }

  function startEdit(item) {
    setEditingId(item.food_item_id);
    setEditItem({
      name: item.name,
      category: item.category || "",
      price: item.price != null ? String(item.price) : "",
      available_from: toTimeInput(item.available_from),
      available_until: toTimeInput(item.available_until),
    });
    setEditError(null);
  }

  async function saveEdit(itemId) {
    setEditError(null);
    try {
      const body = {
        name: editItem.name || undefined,
        category: editItem.category || undefined,
        price: editItem.price !== "" ? parseFloat(editItem.price) : undefined,
        available_from: toApiTime(editItem.available_from),
        available_until: toApiTime(editItem.available_until),
      };
      const updated = await apiFetch(`/api/v1/menu/${itemId}`, {
        method: "PATCH",
        token,
        body: JSON.stringify(body),
      });
      setItems((prev) => prev.map((i) => (i.food_item_id === itemId ? updated : i)));
      setEditingId(null);
    } catch (err) {
      setEditError(err.message);
    }
  }

  async function deleteItem(itemId) {
    if (!confirm("Delete this menu item?")) return;
    try {
      await apiFetch(`/api/v1/menu/${itemId}`, { method: "DELETE", token });
      setItems((prev) => prev.filter((i) => i.food_item_id !== itemId));
    } catch (err) {
      alert(err.message);
    }
  }

  if (loading) return <p>Loading...</p>;
  if (error) return <p style={{ color: "#c00" }}>{error}</p>;

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.25rem" }}>
        <p style={{ fontSize: "0.85rem", color: "#888", margin: 0 }}>
          Restaurant ID: <span style={{ fontFamily: "monospace" }}>{restaurantId}</span>
        </p>
        <Link href="/admin" style={{ fontSize: "0.85rem", color: "#0070f3", textDecoration: "none" }}>
          ← Back to Admin
        </Link>
      </div>

      <button
        onClick={() => setAdding((v) => !v)}
        style={{
          padding: "0.5rem 1rem",
          background: "#0070f3",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          marginBottom: "1.25rem",
        }}
      >
        {adding ? "Cancel" : "+ Add Item"}
      </button>

      {adding && (
        <form
          onSubmit={addItem}
          style={{
            border: "1px solid #e0e0e0",
            borderRadius: "6px",
            padding: "1rem",
            marginBottom: "1.25rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.6rem",
            background: "#fafafa",
          }}
        >
          <input
            placeholder="Name *"
            required
            value={newItem.name}
            onChange={(e) => setNewItem((p) => ({ ...p, name: e.target.value }))}
            style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
          />
          <input
            placeholder="Category"
            value={newItem.category}
            onChange={(e) => setNewItem((p) => ({ ...p, category: e.target.value }))}
            style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
          />
          <input
            type="number"
            placeholder="Price"
            min="0"
            step="0.01"
            value={newItem.price}
            onChange={(e) => setNewItem((p) => ({ ...p, price: e.target.value }))}
            style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
          />
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#555", marginBottom: "0.2rem" }}>
                Available from
              </label>
              <input
                type="time"
                value={newItem.available_from}
                onChange={(e) => setNewItem((p) => ({ ...p, available_from: e.target.value }))}
                style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
              />
            </div>
            <div style={{ flex: 1, minWidth: "140px" }}>
              <label style={{ display: "block", fontSize: "0.8rem", color: "#555", marginBottom: "0.2rem" }}>
                Available until
              </label>
              <input
                type="time"
                value={newItem.available_until}
                onChange={(e) => setNewItem((p) => ({ ...p, available_until: e.target.value }))}
                style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
              />
            </div>
          </div>
          <p style={{ fontSize: "0.78rem", color: "#888", margin: 0 }}>
            Leave both blank for always available. For overnight (e.g. 22:00–02:00) the end time can be earlier than start.
          </p>
          {addError && <p style={{ color: "#c00", fontSize: "0.85rem" }}>{addError}</p>}
          <button
            type="submit"
            style={{ padding: "0.45rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Add
          </button>
        </form>
      )}

      {items.length === 0 && <p style={{ color: "#888" }}>No menu items. Add one above.</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        {items.map((item) => (
          <div
            key={item.food_item_id}
            style={{ border: "1px solid #e0e0e0", borderRadius: "4px", padding: "0.75rem 1rem", background: "#fff" }}
          >
            {editingId === item.food_item_id ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
                  <input
                    value={editItem.name}
                    onChange={(e) => setEditItem((p) => ({ ...p, name: e.target.value }))}
                    placeholder="Name"
                    style={{ ...inputStyle, flex: "2", minWidth: "120px" }}
                  />
                  <input
                    value={editItem.category}
                    onChange={(e) => setEditItem((p) => ({ ...p, category: e.target.value }))}
                    placeholder="Category"
                    style={{ ...inputStyle, flex: "1", minWidth: "100px" }}
                  />
                  <input
                    type="number"
                    value={editItem.price}
                    onChange={(e) => setEditItem((p) => ({ ...p, price: e.target.value }))}
                    placeholder="Price"
                    min="0"
                    step="0.01"
                    style={{ ...inputStyle, width: "90px" }}
                  />
                </div>
                <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
                  <div style={{ flex: 1, minWidth: "140px" }}>
                    <label style={{ display: "block", fontSize: "0.78rem", color: "#555", marginBottom: "0.2rem" }}>
                      Available from
                    </label>
                    <input
                      type="time"
                      value={editItem.available_from}
                      onChange={(e) => setEditItem((p) => ({ ...p, available_from: e.target.value }))}
                      style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
                    />
                  </div>
                  <div style={{ flex: 1, minWidth: "140px" }}>
                    <label style={{ display: "block", fontSize: "0.78rem", color: "#555", marginBottom: "0.2rem" }}>
                      Available until
                    </label>
                    <input
                      type="time"
                      value={editItem.available_until}
                      onChange={(e) => setEditItem((p) => ({ ...p, available_until: e.target.value }))}
                      style={{ ...inputStyle, width: "100%", boxSizing: "border-box" }}
                    />
                  </div>
                </div>
                {editError && <p style={{ color: "#c00", fontSize: "0.8rem", margin: 0 }}>{editError}</p>}
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    onClick={() => saveEdit(item.food_item_id)}
                    style={{ padding: "0.35rem 0.75rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    style={{ padding: "0.35rem 0.75rem", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer", background: "#fff" }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <div>
                  <span style={{ fontWeight: 500 }}>{item.name}</span>
                  {item.category && (
                    <span style={{ color: "#888", fontSize: "0.85rem", marginLeft: "0.5rem" }}>{item.category}</span>
                  )}
                  <span style={{
                    display: "inline-block",
                    marginLeft: "0.6rem",
                    fontSize: "0.78rem",
                    color: item.available_from && item.available_until ? "#666" : "#aaa",
                    fontStyle: "italic",
                  }}>
                    {availabilityText(item.available_from, item.available_until)}
                  </span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  {item.price != null && <span style={{ fontWeight: 600 }}>${item.price.toFixed(2)}</span>}
                  <button
                    onClick={() => startEdit(item)}
                    style={{ padding: "0.25rem 0.55rem", fontSize: "0.8rem", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer", background: "#fff" }}
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => deleteItem(item.food_item_id)}
                    style={{ padding: "0.25rem 0.55rem", fontSize: "0.8rem", border: "1px solid #f5c2c7", borderRadius: "4px", cursor: "pointer", color: "#842029", background: "#fff" }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  );
}

export default function AdminMenuPage() {
  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.6rem", marginBottom: "1.5rem" }}>Manage Menu</h1>
      <Suspense fallback={<p>Loading...</p>}>
        <MenuManager />
      </Suspense>
    </main>
  );
}
