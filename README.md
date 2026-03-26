# SnackOverflow
SnackOverflow is a RESTful backend API for a food delivery platform. It supports multiple user roles (customers and restaurant owners), manages restaurant menus, processes orders, calculates pricing, simulates payments, and generates notifications for key events.

The system is built on a layered architecture (Domain --> Infrastructure --> Application --> Presentation) following SOLID principles and clean code practices. It was built as part of a course project using a real-world food delivery dataset.

## To run the app locally:
### 1. Clone the repository
- git clone https://github.com/aliyanm564/SnackOverflow.git
- cd SnackOverflow

### 2. Create and activate a virtual environment
python -m venv .venv
- source .venv/bin/activate        # macOS/Linux
- .venv\Scripts\activate           # Windows

### 3. Install dependencies
pip install -r requirements.txt

### 4. Create your .env file
cp .env.example .env

Edit .env and set a real JWT_SECRET

### 5. Start the server
uvicorn backend.app.main:app --reload

## To run the app with Docker:
### 1. Create your .env file
cp .env.example .env

Edit .env and set a real JWT_SECRET

### 2. Build and start
docker compose up --build

### 3. Run in background
docker compose up -d

### Useful commands
- docker compose logs -f backend       # tail logs
- docker compose down                  # stop containers
- docker compose down -v               # stop and delete database volume

## API Documentation
 
Once the server is running, interactive API docs are available at:
 
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
 
### Endpoint Summary
 
All protected endpoints require `Authorization: Bearer <token>` in the request header.
 
**Authentication**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/register` | Register a new user account | No |
| POST | `/api/v1/auth/login` | Log in and receive a JWT access token | No |
 
**Users**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/users/me` | Get the currently authenticated user's profile | Yes |
| PATCH | `/api/v1/users/me` | Update the currently authenticated user's profile | Yes |
| GET | `/api/v1/users` | List all users | Owner |
| GET | `/api/v1/users/{customer_id}` | Get a user by ID | Yes |
| PATCH | `/api/v1/users/{customer_id}/role` | Change a user's role | Owner |
| DELETE | `/api/v1/users/{customer_id}` | Delete a user account | Yes |
 
**Restaurants**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/restaurants` | Create a restaurant | Owner |
| GET | `/api/v1/restaurants` | List or search restaurants | Yes |
| GET | `/api/v1/restaurants/{restaurant_id}` | Get a restaurant by ID | Yes |
| PATCH | `/api/v1/restaurants/{restaurant_id}` | Update a restaurant | Owner |
| DELETE | `/api/v1/restaurants/{restaurant_id}` | Delete a restaurant | Owner |
| GET | `/api/v1/restaurants/owner/{owner_id}` | Get restaurants owned by a user | Yes |
 
**Menu**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/restaurants/{restaurant_id}/menu` | Add an item to a restaurant's menu | Owner |
| GET | `/api/v1/restaurants/{restaurant_id}/menu` | Get all menu items for a restaurant | Yes |
| GET | `/api/v1/menu/search` | Search menu items by name across all restaurants | Yes |
| GET | `/api/v1/menu/filter` | Filter menu items by category or price range | Yes |
| GET | `/api/v1/menu/{food_item_id}` | Get a single menu item by ID | Yes |
| PATCH | `/api/v1/menu/{food_item_id}` | Update a menu item | Owner |
| DELETE | `/api/v1/menu/{food_item_id}` | Delete a menu item | Owner |
 
**Orders**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/orders` | Place a new order | Customer |
| GET | `/api/v1/orders` | List orders for the current user | Yes |
| GET | `/api/v1/orders/restaurant/{restaurant_id}` | Get all orders for a restaurant | Owner |
| GET | `/api/v1/orders/{order_id}` | Get a single order by ID | Yes |
| POST | `/api/v1/orders/{order_id}/cancel` | Cancel a pending order | Customer |
 
**Deliveries**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/deliveries/{order_id}` | Assign a delivery to an order | Driver/Owner |
| GET | `/api/v1/deliveries/{order_id}` | Get delivery info for an order | Yes |
| PATCH | `/api/v1/deliveries/{order_id}` | Update a delivery record | Driver/Owner |
| GET | `/api/v1/deliveries` | List all deliveries (paginated) | Yes |
 
**Payments**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/payments/{order_id}` | Process payment for a pending order | Customer |
 
**Notifications**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/v1/notifications` | Get all notifications for the current user | Yes |
| GET | `/api/v1/notifications/unread` | Get unread notifications for the current user | Yes |
| PATCH | `/api/v1/notifications/{notification_id}/read` | Mark a single notification as read | Yes |
| PATCH | `/api/v1/notifications/read-all` | Mark all notifications as read | Yes |
| DELETE | `/api/v1/notifications/{notification_id}` | Delete a notification | Yes |
 
**Health**
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check (used by Docker) | No |
