from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from core.dependencies import get_db, get_current_active_user
from services import interaction_service

router = APIRouter(tags=["Interactions"])

class CommentCreate(BaseModel):
    content: str

@router.post("/news/{news_id}/like")
def toggle_like(
    news_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    return interaction_service.toggle_like(user.id, news_id, db)

@router.get("/news/{news_id}/comments")
def get_comments(
    news_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    return interaction_service.get_comments(news_id, db)

@router.post("/news/{news_id}/comments")
def add_comment(
    news_id: int,
    data: CommentCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    try:
        return interaction_service.add_comment(user.id, news_id, data.content, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/comments/{comment_id}")
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_active_user),
):
    try:
        return interaction_service.delete_comment(user.id, comment_id, db)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))