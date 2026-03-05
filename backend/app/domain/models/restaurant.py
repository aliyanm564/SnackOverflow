class Restaurant:
    def __init__(self, id: int, name: str, location: str):
        self.id = id
        self.name = name
        self.location = location

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location
        }