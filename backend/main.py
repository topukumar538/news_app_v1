from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from database import Base, engine
from routes import auth, admin, user, news, interaction
from core.security import decode_token
from jose import JWTError

Base.metadata.create_all(bind=engine)

app = FastAPI(title="ContentPlatform API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(news.router)
app.include_router(admin.router)
app.include_router(user.router)
app.include_router(interaction.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root(request: Request):
    token = request.cookies.get("token")
    if token:
        try:
            payload = decode_token(token)
            role = payload.get("role")
            if role == "admin":
                return FileResponse("../frontend/admin.html")
            else:
                return FileResponse("../frontend/news.html")
        except JWTError:
            pass
    return FileResponse("../frontend/index.html")

app.mount("/app", StaticFiles(directory="../frontend"), name="frontend")