// Owner: Sukhi
// Feat2-FR4 — Edit an existing restaurant
// Endpoint: PATCH /api/v1/restaurants/{id}
// Body: { name?, location?, description? }
// Requires auth token in header (must be owner)

export default function EditRestaurantPage({ params }) {
  return (
    <main style={{ maxWidth: "600px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Edit Restaurant</h1>
      <p style={{ color: "#888" }}>Edit restaurant form — coming soon</p>
    </main>
  );
}
