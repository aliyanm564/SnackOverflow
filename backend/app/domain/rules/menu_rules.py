from datetime import datetime
from backend.app.domain.models.menu_item import MenuItem

def is_menu_item_available(menu_item):
    now = datetime.now().time()

    start = menu_item.available_from
    end = menu_item.available_until

    if not start and not end:
        return True
    
    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end