"""Модели проекта yacut."""

from datetime import datetime, timezone

from .constants import LINK, SHORT_LINK_MAX
from yacut import db


class URLMap(db.Model):
    """Модель для хранения ссылок в базе данных."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(LINK), nullable=False, index=True)
    short = db.Column(db.String(SHORT_LINK_MAX), nullable=False, unique=True)
    timestamp = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )
