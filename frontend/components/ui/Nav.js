"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, usePathname } from "next/navigation";
import { getUser, clearToken } from "@/lib/auth";

export default function Nav() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    setUser(getUser());
  }, [pathname]);

  function logout() {
    clearToken();
    setUser(null);
    router.push("/");
  }

  const navLink = (href, label) => (
    <Link
      key={href}
      href={href}
      style={{ color: "#ddd", textDecoration: "none", fontSize: "0.9rem", padding: "0.25rem 0.1rem" }}
    >
      {label}
    </Link>
  );

  return (
    <nav style={{
      background: "#111",
      padding: "0.75rem 1.5rem",
      display: "flex",
      alignItems: "center",
      gap: "1.5rem",
    }}>
      <Link href="/" style={{ color: "#fff", fontWeight: 700, fontSize: "1.05rem", textDecoration: "none", flexShrink: 0 }}>
        SnackOverflow
      </Link>

      <div style={{ flex: 1, display: "flex", gap: "1.25rem", alignItems: "center" }}>
        {navLink("/", "Browse")}
        {navLink("/track", "Track")}
        {user && navLink("/orders", "My Orders")}
        {user && navLink("/notifications", "Notifications")}
        {user?.role === "restaurant_owner" && navLink("/admin", "Admin")}
      </div>

      <div style={{ display: "flex", gap: "0.75rem", alignItems: "center" }}>
        {user ? (
          <button
            onClick={logout}
            style={{
              background: "transparent",
              border: "1px solid #555",
              color: "#ccc",
              padding: "0.3rem 0.75rem",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "0.85rem",
            }}
          >
            Logout
          </button>
        ) : (
          <>
            {navLink("/auth/login", "Login")}
            {navLink("/auth/register", "Register")}
          </>
        )}
      </div>
    </nav>
  );
}
