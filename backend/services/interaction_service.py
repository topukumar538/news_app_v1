from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Like, Comment, NEWS
from fastapi import HTTPException

def toggle_like(user_id: int, news_id: int, db: Session):
    news = db.query(NEWS).filter(NEWS.id == news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    existing = db.query(Like).filter(Like.user_id == user_id, Like.news_id == news_id).first()
    if existing:
        db.delete(existing)
        db.commit()
        liked = False
    else:
        db.add(Like(user_id=user_id, news_id=news_id))
        db.commit()
        liked = True
    count = db.query(Like).filter(Like.news_id == news_id).count()
    return {"liked": liked, "like_count": count}

def get_comments(news_id: int, db: Session):
    if not db.query(NEWS).filter(NEWS.id == news_id).first():
        raise HTTPException(status_code=404, detail="News not found")
    comments = (
        db.query(Comment)
        .filter(Comment.news_id == news_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [
        {
            "id": c.id,
            "content": c.content,
            "username": c.user.username,
            "user_id": c.user_id,
            "created_at": str(c.created_at),
        }
        for c in comments
    ]

def add_comment(user_id: int, news_id: int, content: str, db: Session):
    if not content.strip():
        raise ValueError("Comment cannot be empty")
    if not db.query(NEWS).filter(NEWS.id == news_id).first():
        raise HTTPException(status_code=404, detail="News not found")
    comment = Comment(user_id=user_id, news_id=news_id, content=content.strip())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {
        "id": comment.id,
        "content": comment.content,
        "username": comment.user.username,
        "user_id": comment.user_id,
        "created_at": str(comment.created_at),
    }

def delete_comment(user_id: int, comment_id: int, db: Session, is_admin: bool = False):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise ValueError("Comment not found")
    if not is_admin and comment.user_id != user_id:
        raise ValueError("Not authorized")
    db.delete(comment)
    db.commit()
    return {"message": "Comment deleted"}

def get_news_engagement(db: Session, sort: str = "combined"):
    rows = (
        db.query(
            NEWS,
            func.count(Like.id.distinct()).label("like_count"),
            func.count(Comment.id.distinct()).label("comment_count"),
        )
        .outerjoin(Like, Like.news_id == NEWS.id)
        .outerjoin(Comment, Comment.news_id == NEWS.id)
        .group_by(NEWS.id)
        .all()
    )

    result = [
        {
            "id": n.id,
            "title": n.title or n.link,
            "link": n.link,
            "category": n.category,
            "image": n.image or "",
            "like_count": lc,
            "comment_count": cc,
            "created_at": str(n.created_at),
        }
        for n, lc, cc in rows
    ]

    if sort == "likes":
        result.sort(key=lambda x: x["like_count"], reverse=True)
    elif sort == "comments":
        result.sort(key=lambda x: x["comment_count"], reverse=True)
    else:
        result.sort(key=lambda x: x["like_count"] + x["comment_count"], reverse=True)

    return result