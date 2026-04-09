"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken, getUser } from "@/lib/auth";

const inputStyle = {
  padding: "0.45rem 0.65rem",
  border: "1px solid #ccc",
  borderRadius: "4px",
  fontSize: "0.9rem",
  width: "100%",
  boxSizing: "border-box",
};

function formatDate(v) {
  if (!v) return "—";
  return new Date(v).toLocaleDateString();
}

export default function AdminPromosPage() {
  const router = useRouter();
  const token = getToken();
  const user = getUser();

  const [promos, setPromos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    code: "",
    discount_type: "percentage",
    discount_value: "",
    expiry_date: "",
    usage_limit: "",
  });
  const [createError, setCreateError] = useState(null);

  const [assigning, setAssigning] = useState(null);
  const [assignInput, setAssignInput] = useState("");
  const [assignError, setAssignError] = useState(null);

  useEffect(() => {
    if (!token || user?.role !== "restaurant_owner") {
      router.push("/auth/login");
      return;
    }
    fetchPromos();
  }, []);

  async function fetchPromos() {
    try {
      const data = await apiFetch("/api/v1/promos", { token });
      setPromos(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function createPromo(e) {
    e.preventDefault();
    setCreateError(null);
    try {
      const payload = {
        code: form.code,
        discount_type: form.discount_type,
        discount_value: parseFloat(form.discount_value),
        expiry_date: form.expiry_date ? new Date(form.expiry_date).toISOString() : undefined,
        usage_limit: form.usage_limit ? parseInt(form.usage_limit, 10) : undefined,
      };
      const promo = await apiFetch("/api/v1/promos", {
        method: "POST",
        token,
        body: JSON.stringify(payload),
      });
      setPromos((prev) => [promo, ...prev]);
      setForm({ code: "", discount_type: "percentage", discount_value: "", expiry_date: "", usage_limit: "" });
      setCreating(false);
    } catch (err) {
      setCreateError(err.message);
    }
  }

  async function toggleActive(promo) {
    const action = promo.is_active ? "deactivate" : "activate";
    try {
      const updated = await apiFetch(`/api/v1/promos/${promo.promo_id}/${action}`, {
        method: "PATCH",
        token,
      });
      setPromos((prev) => prev.map((p) => (p.promo_id === promo.promo_id ? updated : p)));
    } catch (err) {
      alert(err.message);
    }
  }

  async function assignCustomers(promoId) {
    setAssignError(null);
    const ids = assignInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    if (!ids.length) return;
    try {
      const updated = await apiFetch(`/api/v1/promos/${promoId}/assign`, {
        method: "POST",
        token,
        body: JSON.stringify({ customer_ids: ids }),
      });
      setPromos((prev) => prev.map((p) => (p.promo_id === promoId ? updated : p)));
      setAssigning(null);
      setAssignInput("");
    } catch (err) {
      setAssignError(err.message);
    }
  }

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.6rem", marginBottom: "1.5rem" }}>Admin — Promo Codes</h1>

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
        {creating ? "Cancel" : "+ New Promo Code"}
      </button>

      {creating && (
        <form
          onSubmit={createPromo}
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
          <h2 style={{ fontSize: "1rem", margin: 0 }}>New Promo Code</h2>

          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <div style={{ flex: "2", minWidth: "120px" }}>
              <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.2rem" }}>
                Code *
              </label>
              <input
                required
                placeholder="e.g. SAVE10"
                value={form.code}
                onChange={(e) => setForm((p) => ({ ...p, code: e.target.value.toUpperCase() }))}
                style={inputStyle}
              />
            </div>
            <div style={{ flex: "1", minWidth: "120px" }}>
              <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.2rem" }}>
                Type *
              </label>
              <select
                value={form.discount_type}
                onChange={(e) => setForm((p) => ({ ...p, discount_type: e.target.value }))}
                style={inputStyle}
              >
                <option value="percentage">Percentage (%)</option>
                <option value="flat">Flat ($)</option>
              </select>
            </div>
            <div style={{ flex: "1", minWidth: "100px" }}>
              <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.2rem" }}>
                Value *
              </label>
              <input
                required
                type="number"
                min="0.01"
                step="0.01"
                placeholder={form.discount_type === "percentage" ? "10" : "5.00"}
                value={form.discount_value}
                onChange={(e) => setForm((p) => ({ ...p, discount_value: e.target.value }))}
                style={inputStyle}
              />
            </div>
          </div>

          <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
            <div style={{ flex: "1", minWidth: "140px" }}>
              <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.2rem" }}>
                Expiry date
              </label>
              <input
                type="date"
                value={form.expiry_date}
                onChange={(e) => setForm((p) => ({ ...p, expiry_date: e.target.value }))}
                style={inputStyle}
              />
            </div>
            <div style={{ flex: "1", minWidth: "120px" }}>
              <label style={{ fontSize: "0.8rem", color: "#555", display: "block", marginBottom: "0.2rem" }}>
                Usage limit
              </label>
              <input
                type="number"
                min="1"
                placeholder="Unlimited"
                value={form.usage_limit}
                onChange={(e) => setForm((p) => ({ ...p, usage_limit: e.target.value }))}
                style={inputStyle}
              />
            </div>
          </div>

          {createError && <p style={{ color: "#c00", fontSize: "0.875rem" }}>{createError}</p>}

          <button
            type="submit"
            style={{
              padding: "0.5rem",
              background: "#0070f3",
              color: "#fff",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            Create
          </button>
        </form>
      )}

      {promos.length === 0 && !error && (
        <p style={{ color: "#888" }}>No promo codes yet. Create one above.</p>
      )}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {promos.map((promo) => (
          <div
            key={promo.promo_id}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: "6px",
              padding: "1rem 1.25rem",
              background: "#fff",
            }}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.5rem" }}>
              <div>
                <span style={{ fontWeight: 700, fontSize: "1rem", fontFamily: "monospace" }}>
                  {promo.code}
                </span>
                <span
                  style={{
                    marginLeft: "0.75rem",
                    padding: "0.15rem 0.5rem",
                    borderRadius: "12px",
                    fontSize: "0.75rem",
                    fontWeight: 600,
                    background: promo.is_active ? "#d4edda" : "#f8d7da",
                    color: promo.is_active ? "#155724" : "#721c24",
                  }}
                >
                  {promo.is_active ? "Active" : "Inactive"}
                </span>
              </div>
              <button
                onClick={() => toggleActive(promo)}
                style={{
                  padding: "0.3rem 0.65rem",
                  fontSize: "0.8rem",
                  border: "1px solid #ccc",
                  borderRadius: "4px",
                  cursor: "pointer",
                  background: "#fff",
                }}
              >
                {promo.is_active ? "Deactivate" : "Activate"}
              </button>
            </div>

            <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.875rem", color: "#444", flexWrap: "wrap", marginBottom: "0.5rem" }}>
              <span>
                <strong>Discount:</strong>{" "}
                {promo.discount_type === "percentage"
                  ? `${promo.discount_value}%`
                  : `$${promo.discount_value.toFixed(2)}`}
              </span>
              <span><strong>Used:</strong> {promo.usage_count}{promo.usage_limit ? ` / ${promo.usage_limit}` : ""}</span>
              <span><strong>Expires:</strong> {formatDate(promo.expiry_date)}</span>
              {promo.assigned_customer_ids.length > 0 && (
                <span><strong>Assigned to:</strong> {promo.assigned_customer_ids.length} customer{promo.assigned_customer_ids.length !== 1 ? "s" : ""}</span>
              )}
            </div>

            {assigning === promo.promo_id ? (
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", marginTop: "0.5rem", flexWrap: "wrap" }}>
                <input
                  placeholder="Customer IDs (comma-separated)"
                  value={assignInput}
                  onChange={(e) => setAssignInput(e.target.value)}
                  style={{ ...inputStyle, flex: 1, minWidth: "200px" }}
                />
                <button
                  onClick={() => assignCustomers(promo.promo_id)}
                  style={{ padding: "0.4rem 0.75rem", background: "#0070f3", color: "#fff", border: "none", borderRadius: "4px", cursor: "pointer", fontSize: "0.85rem" }}
                >
                  Assign
                </button>
                <button
                  onClick={() => { setAssigning(null); setAssignInput(""); setAssignError(null); }}
                  style={{ padding: "0.4rem 0.75rem", border: "1px solid #ccc", borderRadius: "4px", cursor: "pointer", fontSize: "0.85rem", background: "#fff" }}
                >
                  Cancel
                </button>
                {assignError && <p style={{ color: "#c00", fontSize: "0.8rem", width: "100%", margin: 0 }}>{assignError}</p>}
              </div>
            ) : (
              <button
                onClick={() => { setAssigning(promo.promo_id); setAssignError(null); }}
                style={{ padding: "0.25rem 0.6rem", fontSize: "0.8rem", border: "1px solid #b3d4fb", borderRadius: "4px", cursor: "pointer", background: "#f0f7ff", color: "#0070f3", marginTop: "0.25rem" }}
              >
                Assign to customers
              </button>
            )}
          </div>
        ))}
      </div>
    </main>
  );
}
