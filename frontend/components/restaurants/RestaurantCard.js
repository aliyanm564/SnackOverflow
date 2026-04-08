// Owner: Sukhi / Temi (shared)
// Used on: app/page.js (browse) and app/restaurants/[id]/page.js (detail)

export default function RestaurantCard({ restaurant }) {
  return (
    <div style={{
      border: "1px solid #e0e0e0",
      borderRadius: "6px",
      padding: "1rem 1.25rem",
      background: "#fff",
    }}>
      <h2 style={{ fontSize: "1.1rem", marginBottom: "0.25rem" }}>
        {restaurant.name || "Unnamed Restaurant"}
      </h2>
      {restaurant.location && (
        <p style={{ color: "#666", fontSize: "0.9rem" }}>{restaurant.location}</p>
      )}
      {restaurant.description && (
        <p style={{ marginTop: "0.5rem", fontSize: "0.875rem", color: "#444" }}>
          {restaurant.description}
        </p>
      )}
    </div>
  );
}
