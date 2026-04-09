"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const data = await apiFetch("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      setToken(data.access_token);
      router.push("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = {
    padding: "0.5rem 0.75rem",
    border: "1px solid #ccc",
    borderRadius: "4px",
    fontSize: "0.95rem",
  };

  return (
    <main style={{ maxWidth: "400px", margin: "4rem auto", padding: "0 1rem" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1.5rem" }}>Login</h1>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          style={inputStyle}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          style={inputStyle}
        />
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
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
      <p style={{ marginTop: "1rem", fontSize: "0.9rem", color: "#555" }}>
        No account?{" "}
        <a href="/auth/register" style={{ color: "#0070f3" }}>
          Register
        </a>
      </p>
    </main>
  );
}
