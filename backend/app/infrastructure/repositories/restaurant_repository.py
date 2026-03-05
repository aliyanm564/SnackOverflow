def get_all_restaurants():
    # Placeholder for fetching all restaurants from the database
    query = "SELECT * FROM restaurants"

def search_restaurants(query: str, limit:int, offset:int):
    sql = """
    SELECT *
    FROM restaurants
    WHERE name ILIKE %s
    LIMIT %s OFFSET %s 
    """