from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from models import NEWS, Like, Comment
from schemas.news import NEWSCreate, NEWSUpdate

CATEGORIES = ["National", "International", "Sports", "Business"]

def create_news(data: NEWSCreate, db: Session):
    if data.category not in CATEGORIES:
        raise HTTPException(status_code=400, detail=f"Category must be one of: {', '.join(CATEGORIES)}")
    news = NEWS(
        link=data.link,
        category=data.category,
        title=data.title or None,
        image=data.image or None,
    )
    db.add(news)
    db.commit()
    db.refresh(news)
    return news

def update_news(news_id: int, data: NEWSUpdate, db: Session):
    news = db.query(NEWS).filter(NEWS.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    if data.title is not None:
        news.title = data.title
    if data.link is not None:
        news.link = data.link
    if data.category is not None:
        if data.category not in CATEGORIES:
            raise HTTPException(status_code=400, detail=f"Category must be one of: {', '.join(CATEGORIES)}")
        news.category = data.category
    if data.image is not None:
        news.image = data.image
    db.commit()
    db.refresh(news)
    return news

def delete_news(news_id: int, db: Session):
    news = db.query(NEWS).filter(NEWS.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(news)
    db.commit()
    return {"message": "News deleted"}

def get_news(db: Session, user_id: int):
    # Pre-load all user likes in one query for efficiency
    user_liked_ids = set()
    if user_id:
        rows = db.query(Like.news_id).filter(Like.user_id == user_id).all()
        user_liked_ids = {r.news_id for r in rows}

    result = {}
    for cat in CATEGORIES:
        rows = (
            db.query(
                NEWS,
                func.count(Like.id.distinct()).label("like_count"),
                func.count(Comment.id.distinct()).label("comment_count"),
            )
            .outerjoin(Like, Like.news_id == NEWS.id)
            .outerjoin(Comment, Comment.news_id == NEWS.id)
            .filter(NEWS.category == cat)
            .group_by(NEWS.id)
            .order_by(NEWS.created_at.desc())
            .all()
        )
        result[cat.lower()] = [
            {
                "id": n.id,
                "link": n.link,
                "category": n.category,
                "title": n.title or "",
                "image": n.image or "",
                "created_at": str(n.created_at),
                "like_count": like_count,
                "comment_count": comment_count,
                "user_liked": n.id in user_liked_ids,
            }
            for n, like_count, comment_count in rows
        ]
    return result