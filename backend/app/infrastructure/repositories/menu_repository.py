def get_menu_by_restaurant(restaurant_id: int, limit: int, offset: int):
    query = """
        SELECT *
        FROM menu_items
        WHERE restaurant_id = %s
        LIMIT %s OFFSET %s
    """

def search_menu_items(restaurant_id: int, query: str, limit: int, offset: int):
    sql = """
        SELECT *
        FROM menu_items
        WHERE restaurant_id = %s
        AND name ILIKE %s
        LIMIT %s OFFSET %s
    """