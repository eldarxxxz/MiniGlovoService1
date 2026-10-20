from fastapi import FastAPI
from database import engine, Base
from models.user import UserProfile
from routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MiniGlovoService1",
    description="User Profile API",
    version="1.0.0"
)

app.include_router(auth_router)

@app.get("/")
def home():
    return {"message": "Mini Glovo Service 1 is working!"}

