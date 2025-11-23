from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserAdmin(BaseModel):
    """User representation for admin views."""
    id: int
    email: EmailStr
    username: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Partial update for user admin actions."""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserStats(BaseModel):
    """Aggregated statistics about users."""
    total_users: int
    active_users: int
    admin_users: int
    new_users_this_month: int
