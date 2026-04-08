import { apiFetch } from "@/lib/api";
import RestaurantCard from "@/components/restaurants/RestaurantCard";

async function getRestaurants() {
  try {
    return await apiFetch("/api/v1/restaurants?limit=50");
  } catch (err) {
    return { error: err.message };
  }
}

export default async function Home() {
  const data = await getRestaurants();

  return (
    <main style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.75rem", marginBottom: "0.25rem" }}>SnackOverflow</h1>
      <p style={{ color: "#555", marginBottom: "2rem" }}>Browse restaurants</p>

      {data.error ? (
        <p style={{ color: "#c00" }}>Could not load restaurants: {data.error}</p>
      ) : data.length === 0 ? (
        <p style={{ color: "#888" }}>No restaurants found.</p>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          {data.map((r) => (
            <RestaurantCard key={r.restaurant_id} restaurant={r} />
          ))}
        </div>
      )}
    </main>
  );
}
