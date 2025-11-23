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


# --------------------------------------------------------------------
# Landing content (CMS)
# --------------------------------------------------------------------


class LandingContentBase(BaseModel):
    hero_title: str
    hero_subtitle: str

    feature1_title: str
    feature1_text: str

    feature2_title: str
    feature2_text: str

    feature3_title: str
    feature3_text: str

    how1_title: str
    how1_text: str

    how2_title: str
    how2_text: str

    how3_title: str
    how3_text: str

    cta_title: str
    cta_subtitle: str


class LandingContentOut(LandingContentBase):
    id: int

    class Config:
        from_attributes = True  # pour SQLAlchemy 2.x


class LandingContentUpdate(LandingContentBase):
    """Payload complet pour l'update (PUT) depuis l'admin."""
    pass
