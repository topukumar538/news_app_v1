from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.dependencies import get_db, get_current_user, admin_only
from schemas.news import NEWSCreate
from services import news_service

router = APIRouter(tags=["News"])

@router.get("/news")
def get_news(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return news_service.get_news(db)

@router.post("/news")
def create_news(data: NEWSCreate, db: Session = Depends(get_db), user=Depends(admin_only)):
    return news_service.create_news(data, db)

@router.delete("/news/{news_id}")
def delete_news(news_id: int, db: Session = Depends(get_db), user=Depends(admin_only)):
    return news_service.delete_news(news_id, db)