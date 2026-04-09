from datetime import datetime


def is_menu_item_available(menu_item) -> bool:
    start = menu_item.available_from
    end = menu_item.available_until

    if start is None or end is None:
        return True

    now = datetime.now().time()

    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end
