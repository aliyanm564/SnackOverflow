"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

const inputStyle = {
  width: "100%",
  padding: "0.45rem 0.65rem",
  border: "1px solid #ccc",
  borderRadius: "4px",
  boxSizing: "border-box",
  fontSize: "0.9rem",
};

export default function AdminPage() {
  const router = useRouter();
  const token = getToken();
  const user = getUser();

  const [restaurants, setRestaurants] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [creating, setCreating] = useState(false);
  const [newForm, setNewForm] = useState({ name: "", location: "", description: "" });
  const [createError, setCreateError] = useState(null);

  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});
  const [editError, setEditError] = useState(null);

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
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function createRestaurant(e) {
    e.preventDefault();
    setCreateError(null);
    try {
      const r = await apiFetch("/api/v1/restaurants", {
        method: "POST",
        token,
        body: JSON.stringify({
          name: newForm.name,
          location: newForm.location || undefined,
          description: newForm.description || undefined,
        }),
      });
      setRestaurants((prev) => [r, ...prev]);
      setNewForm({ name: "", location: "", description: "" });
      setCreating(false);
    } catch (err) {
      setCreateError(err.message);
    }
  }

  function startEdit(r) {
    setEditingId(r.restaurant_id);
    setEditForm({
      name: r.name || "",
      location: r.location || "",
      description: r.description || "",
    });
    setEditError(null);
  }

  async function saveEdit(restaurantId) {
    setEditError(null);
    try {
      const updated = await apiFetch(`/api/v1/restaurants/${restaurantId}`, {
        method: "PATCH",
        token,
        body: JSON.stringify({
          name: editForm.name || undefined,
          location: editForm.location || undefined,
          description: editForm.description || undefined,
        }),
      });
      setRestaurants((prev) =>
        prev.map((r) => (r.restaurant_id === restaurantId ? updated : r))
      );
      setEditingId(null);
    } catch (err) {
      setEditError(err.message);
    }
  }

  async function deleteRestaurant(restaurantId) {
    if (!confirm("Delete this restaurant? This cannot be undone.")) return;
    try {
      await apiFetch(`/api/v1/restaurants/${restaurantId}`, { method: "DELETE", token });
      setRestaurants((prev) => prev.filter((r) => r.restaurant_id !== restaurantId));
    } catch (err) {
      alert(err.message);
    }
  }

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.6rem" }}>Admin — My Restaurants</h1>
        <div style={{ display: "flex", gap: "0.5rem" }}>
          <Link href="/admin/orders" style={{ fontSize: "0.875rem", padding: "0.4rem 0.85rem", background: "#fff8e1", color: "#856404", border: "1px solid #ffc107", borderRadius: "4px", textDecoration: "none" }}>
            Orders →
          </Link>
          <Link href="/admin/promos" style={{ fontSize: "0.875rem", padding: "0.4rem 0.85rem", background: "#f0f7ff", color: "#0070f3", border: "1px solid #b3d4fb", borderRadius: "4px", textDecoration: "none" }}>
            Promo Codes →
          </Link>
          <Link href="/admin/reviews" style={{ fontSize: "0.875rem", padding: "0.4rem 0.85rem", background: "#f0fff4", color: "#155724", border: "1px solid #b2dfdb", borderRadius: "4px", textDecoration: "none" }}>
            Reviews →
          </Link>
        </div>
      </div>

      {error && <p style={{ color: "#c00", marginBottom: "1rem" }}>{error}</p>}

      <button
        onClick={() => setCreating((v) => !v)}
        style={{
          padding: "0.5rem 1rem",
          background: "#0070f3",
          color: "#fff",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
          marginBottom: "1.5rem",
        }}
      >
        {creating ? "Cancel" : "+ Add Restaurant"}
      </button>

      {creating && (
        <form
          onSubmit={createRestaurant}
          style={{
            border: "1px solid #e0e0e0",
            borderRadius: "6px",
            padding: "1.25rem",
            marginBottom: "1.5rem",
            display: "flex",
            flexDirection: "column",
            gap: "0.65rem",
            background: "#fafafa",
          }}
        >
          <h2 style={{ fontSize: "1rem", margin: 0 }}>New Restaurant</h2>
          <input
            placeholder="Name *"
            required
            value={newForm.name}
            onChange={(e) => setNewForm((p) => ({ ...p, name: e.target.value }))}
            style={inputStyle}
          />
          <input
            placeholder="Location"
            value={newForm.location}
            onChange={(e) => setNewForm((p) => ({ ...p, location: e.target.value }))}
            style={inputStyle}
          />
          <input
            placeholder="Description"
            value={newForm.description}
            onChange={(e) => setNewForm((p) => ({ ...p, description: e.target.value }))}
            style={inputStyle}
          />
          {createError && <p style={{ color: "#c00", fontSize: "0.9rem" }}>{createError}</p>}
          <button
            type="submit"
            style={{ padding: "0.5rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
          >
            Create
          </button>
        </form>
      )}

      {restaurants.length === 0 && !error && (
        <p style={{ color: "#888" }}>No restaurants yet. Create one above.</p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {restaurants.map((r) => (
          <div
            key={r.restaurant_id}
            style={{ border: "1px solid #e0e0e0", borderRadius: "6px", padding: "1.25rem", background: "#fff" }}
          >
            {editingId === r.restaurant_id ? (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                <input
                  value={editForm.name}
                  onChange={(e) => setEditForm((p) => ({ ...p, name: e.target.value }))}
                  placeholder="Name"
                  style={inputStyle}
                />
                <input
                  value={editForm.location}
                  onChange={(e) => setEditForm((p) => ({ ...p, location: e.target.value }))}
                  placeholder="Location"
                  style={inputStyle}
                />
                <input
                  value={editForm.description}
                  onChange={(e) => setEditForm((p) => ({ ...p, description: e.target.value }))}
                  placeholder="Description"
                  style={inputStyle}
                />
                {editError && <p style={{ color: "#c00", fontSize: "0.85rem" }}>{editError}</p>}
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button
                    onClick={() => saveEdit(r.restaurant_id)}
                    style={{ padding: "0.4rem 0.9rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer" }}
                  >
                    Save
                  </button>
                  <button
                    onClick={() => setEditingId(null)}
                    style={{ padding: "0.4rem 0.9rem", background: "#fff", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer" }}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.4rem" }}>
                  <h2 style={{ fontSize: "1.1rem", margin: 0 }}>{r.name || "Unnamed"}</h2>
                  <div style={{ display: "flex", gap: "0.4rem" }}>
                    <button
                      onClick={() => startEdit(r)}
                      style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer", background: "#fff" }}
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => deleteRestaurant(r.restaurant_id)}
                      style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem", border: "1px solid #f5c2c7", borderRadius: "4px", cursor: "pointer", color: "#842029", background: "#fff" }}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                {r.location && <p style={{ color: "#666", fontSize: "0.9rem", margin: "0 0 0.2rem" }}>{r.location}</p>}
                {r.description && <p style={{ fontSize: "0.875rem", color: "#444", margin: "0 0 0.75rem" }}>{r.description}</p>}
                <Link
                  href={`/admin/menu?restaurant=${r.restaurant_id}`}
                  style={{
                    fontSize: "0.85rem",
                    padding: "0.3rem 0.75rem",
                    background: "#f0f7ff",
                    color: "#0070f3",
                    border: "1px solid #b3d4fb",
                    borderRadius: "4px",
                    textDecoration: "none",
                    display: "inline-block",
                  }}
                >
                  Manage Menu →
                </Link>
              </>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
