// Owner: Aman
// Feat4-FR4, FR5 — Order detail view
// Endpoint: GET /api/v1/orders/{order_id}
// Also shows delivery status: GET /api/v1/orders/{order_id}/delivery
// Requires auth token in header

export default function OrderDetailPage({ params }) {
  return (
    <main style={{ maxWidth: "700px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ marginBottom: "1.5rem" }}>Order Detail</h1>
      <p style={{ color: "#888" }}>Order detail — coming soon</p>
    </main>
  );
}
