from pydantic import BaseModel
from typing import Optional

class NEWSCreate(BaseModel):
    link: str
    category: str
    title: Optional[str] = None
    image: Optional[str] = None