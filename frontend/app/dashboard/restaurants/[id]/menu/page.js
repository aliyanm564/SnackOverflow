// Owner: Sukhi
// Feat2-FR5 — Manage menu items for a restaurant
// Endpoint: GET    /api/v1/restaurants/{id}/menu-items
// Endpoint: POST   /api/v1/restaurants/{id}/menu-items
// Endpoint: PATCH  /api/v1/menu-items/{item_id}
// Endpoint: DELETE /api/v1/menu-items/{item_id}
// Requires auth token in header (must be restaurant owner)

export default function ManageMenuPage({ params }) {
  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Manage Menu</h1>
      <p style={{ color: "#888" }}>Menu management — coming soon</p>
    </main>
  );
}
