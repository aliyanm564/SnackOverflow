// Owner: Sukhi
// Feat2-FR4 — Create a new restaurant
// Endpoint: POST /api/v1/restaurants
// Body: { name, location, description }
// Requires auth token in header (restaurant_owner role)

export default function NewRestaurantPage() {
  return (
    <main style={{ maxWidth: "600px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Add Restaurant</h1>
      <p style={{ color: "#888" }}>Create restaurant form — coming soon</p>
    </main>
  );
}
