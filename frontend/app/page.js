export default function Home() {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

  return (
    <main style={{ padding: "2rem" }}>
      <h1>SnackOverflow Frontend Running</h1>
      <p style={{ marginTop: "0.5rem", color: "#555" }}>
        API base: <code>{apiBase}</code>
      </p>
      <div style={{ marginTop: "2rem", display: "flex", gap: "1rem" }}>
        <a href={`${apiBase}/docs`} target="_blank" rel="noreferrer"
          style={{ padding: "0.5rem 1rem", background: "#0070f3", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>
          API Docs
        </a>
        <a href={`${apiBase}/health`} target="_blank" rel="noreferrer"
          style={{ padding: "0.5rem 1rem", background: "#333", color: "#fff", borderRadius: "4px", textDecoration: "none" }}>
          Health Check
        </a>
      </div>
    </main>
  );
}
