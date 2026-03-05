class MenuItem:
    def __init__(self, id: int, name: str, price: float, restaurant_id: int):
        self.id = id
        self.name = name
        self.price = price
        self.restaurant_id = restaurant_id

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "restaurant_id": self.restaurant_id
        }