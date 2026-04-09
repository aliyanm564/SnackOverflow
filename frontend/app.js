const state = {
  items: [],
};

const apiBaseInput = document.getElementById("apiBase");
const tokenInput = document.getElementById("token");
const statusText = document.getElementById("statusText");
const menuList = document.getElementById("menuList");

document.getElementById("loginForm").addEventListener("submit", onLogin);
document.getElementById("menuForm").addEventListener("submit", onLoadMenu);
document.getElementById("searchForm").addEventListener("submit", onSearch);
document.getElementById("filterForm").addEventListener("submit", onFilter);

tokenInput.value = localStorage.getItem("snackoverflow_token") || "";

function getApiBase() {
  return apiBaseInput.value.trim().replace(/\/+$/, "");
}

function getToken() {
  return tokenInput.value.trim();
}

function saveToken() {
  const token = getToken();
  localStorage.setItem("snackoverflow_token", token);
}

async function apiRequest(path, options = {}) {
  saveToken();
  const token = getToken();
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${getApiBase()}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let message = `${response.status} ${response.statusText}`;
    try {
      const body = await response.json();
      if (body?.detail) {
        message = body.detail;
      }
    } catch (error) {
      // Ignore non-JSON error bodies.
    }
    throw new Error(message);
  }

  if (response.status === 204) {
    return null;
  }
  return response.json();
}

async function onLogin(event) {
  event.preventDefault();
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  try {
    statusText.textContent = "Logging in...";
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    tokenInput.value = data.access_token;
    saveToken();
    statusText.textContent = "Login successful.";
  } catch (error) {
    statusText.textContent = `Login failed: ${error.message}`;
  }
}

async function onLoadMenu(event) {
  event.preventDefault();
  const restaurantId = document.getElementById("restaurantId").value.trim();
  if (!restaurantId) {
    statusText.textContent = "Please provide a restaurant ID.";
    return;
  }

  try {
    statusText.textContent = "Loading menu...";
    const items = await apiRequest(`/restaurants/${restaurantId}/menu`);
    state.items = items;
    renderItems(items);
    statusText.textContent = `Loaded ${items.length} item(s).`;
  } catch (error) {
    statusText.textContent = `Failed to load menu: ${error.message}`;
  }
}

async function onSearch(event) {
  event.preventDefault();
  const query = document.getElementById("searchQuery").value.trim();
  if (!query) {
    renderItems(state.items);
    statusText.textContent = "Search query empty. Showing current items.";
    return;
  }

  try {
    statusText.textContent = "Searching items...";
    const items = await apiRequest(`/menu/search?q=${encodeURIComponent(query)}`);
    renderItems(items);
    statusText.textContent = `Search found ${items.length} item(s).`;
  } catch (error) {
    statusText.textContent = `Search failed: ${error.message}`;
  }
}

async function onFilter(event) {
  event.preventDefault();
  const category = document.getElementById("category").value.trim();
  const minPrice = document.getElementById("minPrice").value.trim();
  const maxPrice = document.getElementById("maxPrice").value.trim();

  const queryParams = new URLSearchParams();
  if (category) {
    queryParams.set("category", category);
  } else if (minPrice && maxPrice) {
    queryParams.set("min_price", minPrice);
    queryParams.set("max_price", maxPrice);
  }

  try {
    statusText.textContent = "Filtering items...";
    const suffix = queryParams.toString();
    const path = suffix ? `/menu/filter?${suffix}` : "/menu/filter";
    const items = await apiRequest(path);
    renderItems(items);
    statusText.textContent = `Filter returned ${items.length} item(s).`;
  } catch (error) {
    statusText.textContent = `Filter failed: ${error.message}`;
  }
}

function renderItems(items) {
  menuList.innerHTML = "";

  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.className = "menu-item";
    li.textContent = "No menu items found.";
    menuList.appendChild(li);
    return;
  }

  items.forEach((item) => {
    const li = document.createElement("li");
    li.className = "menu-item";
    li.innerHTML = `
      <h3>${escapeHtml(item.name)}</h3>
      <p class="muted">Category: ${escapeHtml(item.category || "N/A")}</p>
      <p class="muted">Price: ${formatPrice(item.price)}</p>
      <p class="muted">Item ID: ${escapeHtml(item.food_item_id)}</p>
      <p class="muted">Restaurant ID: ${escapeHtml(item.restaurant_id)}</p>
    `;
    menuList.appendChild(li);
  });
}

function formatPrice(value) {
  if (value === null || value === undefined) {
    return "N/A";
  }
  return `$${Number(value).toFixed(2)}`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
