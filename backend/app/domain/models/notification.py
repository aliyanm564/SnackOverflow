from datetime import datetime

from pydantic import BaseModel


class Notification(BaseModel):
    notification_id: int | None = None
    user_id: str
    event_type: str
    message: str
    created_at: datetime
    is_read: bool = False
