from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.enums import Role
from app.models.entities import User
from app.models.photo_gallery import PhotoGalleryAlbum, PhotoGalleryImage
from app.schemas.dto import (
    PhotoGalleryAlbumCreate,
    PhotoGalleryAlbumRead,
    PhotoGalleryImageCreate,
    PhotoGalleryImageRead,
)

router = APIRouter(prefix="/photo-gallery", tags=["Photo Gallery"])


@router.post("/albums", response_model=PhotoGalleryAlbumRead)
def create_album(
    payload: PhotoGalleryAlbumCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    society_id = current_user.society_id
    if current_user.role == Role.ADMIN:
        society_id = society_id or 1

    album = PhotoGalleryAlbum(
        society_id=society_id,
        title=payload.title,
        description=payload.description,
        cover_image_url=payload.cover_image_url,
        is_published=payload.is_published,
        sort_order=payload.sort_order,
        created_by_user_id=current_user.id,
    )
    db.add(album)
    db.commit()
    db.refresh(album)
    return album


@router.get("/albums", response_model=list[PhotoGalleryAlbumRead])
def list_albums(
    society_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(PhotoGalleryAlbum)
    if society_id:
        query = query.filter(PhotoGalleryAlbum.society_id == society_id)
    elif current_user.society_id:
        query = query.filter(PhotoGalleryAlbum.society_id == current_user.society_id)

    albums = query.order_by(PhotoGalleryAlbum.sort_order, PhotoGalleryAlbum.created_at.desc()).all()

    # Attach image count
    result = []
    for album in albums:
        album_dict = {
            "id": album.id,
            "society_id": album.society_id,
            "title": album.title,
            "description": album.description,
            "cover_image_url": album.cover_image_url,
            "is_published": album.is_published,
            "sort_order": album.sort_order,
            "created_by_user_id": album.created_by_user_id,
            "created_at": album.created_at,
            "updated_at": album.updated_at,
            "image_count": db.query(func.count(PhotoGalleryImage.id))
                .filter(PhotoGalleryImage.album_id == album.id, PhotoGalleryImage.is_published == True)
                .scalar() or 0,
        }
        result.append(PhotoGalleryAlbumRead(**album_dict))

    return result


@router.get("/albums/{album_id}", response_model=PhotoGalleryAlbumRead)
def get_album(album_id: int, db: Session = Depends(get_db)):
    album = db.get(PhotoGalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    image_count = db.query(func.count(PhotoGalleryImage.id))\
        .filter(PhotoGalleryImage.album_id == album.id, PhotoGalleryImage.is_published == True)\
        .scalar() or 0

    album_dict = {
        "id": album.id,
        "society_id": album.society_id,
        "title": album.title,
        "description": album.description,
        "cover_image_url": album.cover_image_url,
        "is_published": album.is_published,
        "sort_order": album.sort_order,
        "created_by_user_id": album.created_by_user_id,
        "created_at": album.created_at,
        "updated_at": album.updated_at,
        "image_count": image_count,
    }
    return PhotoGalleryAlbumRead(**album_dict)


@router.put("/albums/{album_id}", response_model=PhotoGalleryAlbumRead)
def update_album(
    album_id: int,
    payload: PhotoGalleryAlbumCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    album = db.get(PhotoGalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    album.title = payload.title
    album.description = payload.description
    album.cover_image_url = payload.cover_image_url
    album.is_published = payload.is_published
    album.sort_order = payload.sort_order
    album.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(album)
    return album


@router.delete("/albums/{album_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_album(
    album_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    album = db.get(PhotoGalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    # Delete associated images
    db.query(PhotoGalleryImage).filter(PhotoGalleryImage.album_id == album_id).delete()
    db.delete(album)
    db.commit()


@router.post("/images", response_model=PhotoGalleryImageRead)
def create_image(
    payload: PhotoGalleryImageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    album = db.get(PhotoGalleryAlbum, payload.album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    image = PhotoGalleryImage(
        album_id=payload.album_id,
        title=payload.title,
        image_url=payload.image_url,
        thumbnail_url=payload.thumbnail_url,
        description=payload.description,
        sort_order=payload.sort_order,
        uploaded_by_user_id=current_user.id,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.get("/albums/{album_id}/images", response_model=list[PhotoGalleryImageRead])
def list_album_images(album_id: int, db: Session = Depends(get_db)):
    album = db.get(PhotoGalleryAlbum, album_id)
    if not album:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Album not found")

    return (
        db.query(PhotoGalleryImage)
        .filter(PhotoGalleryImage.album_id == album_id, PhotoGalleryImage.is_published == True)
        .order_by(PhotoGalleryImage.sort_order, PhotoGalleryImage.created_at.desc())
        .all()
    )


@router.delete("/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    image = db.get(PhotoGalleryImage, image_id)
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

    if current_user.role not in (Role.ADMIN, Role.SOCIETY_ADMIN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    db.delete(image)
    db.commit()