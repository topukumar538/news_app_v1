from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import NEWS
from schemas.news import NEWSCreate

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

def delete_news(news_id: int, db: Session):
    news = db.query(NEWS).filter(NEWS.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    db.delete(news)
    db.commit()
    return {"message": "News deleted"}

def get_news(db: Session):
    result = {}
    for cat in CATEGORIES:
        items = db.query(NEWS).filter(NEWS.category == cat).order_by(NEWS.created_at.desc()).all()
        result[cat.lower()] = [
            {
                "id": n.id,
                "link": n.link,
                "category": n.category,
                "title": n.title or "",
                "image": n.image or "",
                "created_at": str(n.created_at),
            }
            for n in items
        ]
    return result