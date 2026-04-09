"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    password: "",
    name: "",
    role: "customer",
    location: "",
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  function update(field) {
    return (e) => setForm((prev) => ({ ...prev, [field]: e.target.value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await apiFetch("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          email: form.email,
          password: form.password,
          name: form.name || undefined,
          role: form.role,
          location: form.location || undefined,
        }),
      });
      router.push("/auth/login");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = {
    width: "100%",
    padding: "0.5rem 0.75rem",
    border: "1px solid #ccc",
    borderRadius: "4px",
    boxSizing: "border-box",
    fontSize: "0.95rem",
  };

  const label = (text) => (
    <span style={{ display: "block", fontSize: "0.85rem", marginBottom: "0.25rem", color: "#555" }}>
      {text}
    </span>
  );

  return (
    <main style={{ maxWidth: "400px", margin: "4rem auto", padding: "0 1rem" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Create Account</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
        <div>
          {label("Email *")}
          <input type="email" value={form.email} onChange={update("email")} required style={inputStyle} />
        </div>
        <div>
          {label("Password (min 6 characters) *")}
          <input type="password" value={form.password} onChange={update("password")} required minLength={6} style={inputStyle} />
        </div>
        <div>
          {label("Name")}
          <input type="text" value={form.name} onChange={update("name")} style={inputStyle} />
        </div>
        <div>
          {label("Location")}
          <input type="text" value={form.location} onChange={update("location")} style={inputStyle} />
        </div>
        <div>
          {label("Role")}
          <select value={form.role} onChange={update("role")} style={inputStyle}>
            <option value="customer">Customer</option>
            <option value="restaurant_owner">Restaurant Owner</option>
          </select>
        </div>

        {error && <p style={{ color: "#c00", fontSize: "0.9rem" }}>{error}</p>}

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: "0.6rem",
            background: "#0070f3",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: loading ? "not-allowed" : "pointer",
            fontSize: "0.95rem",
          }}
        >
          {loading ? "Creating account..." : "Create Account"}
        </button>
      </form>
      <p style={{ marginTop: "1rem", fontSize: "0.9rem", color: "#555" }}>
        Already have an account?{" "}
        <a href="/auth/login" style={{ color: "#0070f3" }}>
          Login
        </a>
      </p>
    </main>
  );
}
