"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getToken } from "@/lib/auth";

function formatDate(v) {
  if (!v) return "";
  return new Date(v).toLocaleString();
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();
  const token = getToken();

  useEffect(() => {
    if (!token) { router.push("/auth/login"); return; }
    fetchNotifications();
  }, []);

  async function fetchNotifications() {
    try {
      const data = await apiFetch("/api/v1/notifications", { token });
      setNotifications(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function markRead(notificationId) {
    try {
      const updated = await apiFetch(`/api/v1/notifications/${notificationId}/read`, {
        method: "PATCH",
        token,
      });
      setNotifications((prev) =>
        prev.map((n) => (n.notification_id === notificationId ? updated : n))
      );
    } catch {
      // silently fail
    }
  }

  async function markAllRead() {
    try {
      await apiFetch("/api/v1/notifications/read-all", { method: "PATCH", token });
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
    } catch {
      // silently fail
    }
  }

  async function remove(notificationId) {
    try {
      await apiFetch(`/api/v1/notifications/${notificationId}`, { method: "DELETE", token });
      setNotifications((prev) => prev.filter((n) => n.notification_id !== notificationId));
    } catch {
      // silently fail
    }
  }

  const unread = notifications.filter((n) => !n.is_read).length;

  if (loading) return <main style={{ padding: "2rem" }}><p>Loading...</p></main>;
  if (error) return <main style={{ padding: "2rem" }}><p style={{ color: "#c00" }}>{error}</p></main>;

  return (
    <main style={{ maxWidth: "700px", margin: "0 auto", padding: "2rem 1rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.6rem" }}>
          Notifications
          {unread > 0 && (
            <span style={{ fontSize: "1rem", color: "#0070f3", fontWeight: 400, marginLeft: "0.5rem" }}>
              ({unread} unread)
            </span>
          )}
        </h1>
        {unread > 0 && (
          <button
            onClick={markAllRead}
            style={{
              padding: "0.35rem 0.75rem",
              background: "transparent",
              border: "1px solid #ccc",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.85rem",
            }}
          >
            Mark all read
          </button>
        )}
      </div>

      {notifications.length === 0 && <p style={{ color: "#888" }}>No notifications.</p>}

      <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
        {notifications.map((n) => (
          <div
            key={n.notification_id}
            style={{
              border: "1px solid #e0e0e0",
              borderRadius: "6px",
              padding: "0.85rem 1rem",
              background: n.is_read ? "#fff" : "#f0f7ff",
              display: "flex",
              gap: "1rem",
              alignItems: "flex-start",
            }}
          >
            <div style={{ flex: 1 }}>
              <p style={{ fontWeight: n.is_read ? 400 : 600, marginBottom: "0.2rem" }}>{n.message}</p>
              <p style={{ fontSize: "0.8rem", color: "#888" }}>
                {formatDate(n.created_at)} · {n.event_type}
              </p>
            </div>
            <div style={{ display: "flex", gap: "0.4rem", flexShrink: 0 }}>
              {!n.is_read && (
                <button
                  onClick={() => markRead(n.notification_id)}
                  style={{
                    padding: "0.2rem 0.5rem",
                    fontSize: "0.8rem",
                    border: "1px solid #ccc",
                    borderRadius: "4px",
                    cursor: "pointer",
                    background: "#fff",
                  }}
                >
                  Read
                </button>
              )}
              <button
                onClick={() => remove(n.notification_id)}
                style={{
                  padding: "0.2rem 0.45rem",
                  fontSize: "0.8rem",
                  border: "1px solid #f5c2c7",
                  borderRadius: "4px",
                  cursor: "pointer",
                  background: "#fff",
                  color: "#842029",
                }}
              >
                ✕
              </button>
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
