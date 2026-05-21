from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class PhotoGalleryAlbum(Base):
    """Photo gallery albums - from external repo's photo gallery feature"""
    __tablename__ = "photo_gallery_albums"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    cover_image_url: Mapped[str | None] = mapped_column(String(500))
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PhotoGalleryImage(Base):
    """Individual images within an album"""
    __tablename__ = "photo_gallery_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("photo_gallery_albums.id"), nullable=False, index=True)
    title: Mapped[str | None] = mapped_column(String(200))
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class NoticeEnhanced(Base):
    """Enhanced notice board with types, categories, file attachments - from external repo"""
    __tablename__ = "notices_enhanced"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    society_id: Mapped[int] = mapped_column(ForeignKey("societies.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    notice_type: Mapped[str] = mapped_column(String(50), default="general", index=True)  # general, event, emergency, meeting, holiday
    message: Mapped[str] = mapped_column(Text, nullable=False)
    file_url: Mapped[str | None] = mapped_column(String(500))  # attachment
    is_urgent: Mapped[bool] = mapped_column(Boolean, default=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    published_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    published_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)