from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from database import get_db
from models.user import UserProfile
from schemas.user import UserCreate, UserResponse, UserLogin
from datetime import datetime, timedelta, timezone
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security
from typing import List

router = APIRouter(prefix="/auth", tags=["Auth"])
security = HTTPBearer()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "mini-glovo-secret-key-change-this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(UserProfile).filter(
        (UserProfile.username == user.username) |
        (UserProfile.email == user.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    hashed_password = pwd_context.hash(user.password)

    new_user = UserProfile(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=hashed_password,
        email=str(user.email),
        user_role=user.user_role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserProfile).filter(
        UserProfile.username == user.username
    ).first()

    if not db_user or not pwd_context.verify(user.password, db_user.password):
        raise HTTPException(
            status_code=401,
            detail="Неправильный username или password"
        )

    access_token = create_access_token({"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username = payload.get("sub")

        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user = db.query(UserProfile).filter(
        UserProfile.username == username
    ).first()

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    return user


@router.get("/check")
def check_token(
    current_user: UserProfile = Depends(get_current_user)
):
    return {
        "message": "Token is valid",
        "username": current_user.username
    }


@router.get("/me/profile")
def get_my_profile(
    current_user: UserProfile = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "username": current_user.username,
        "email": current_user.email,
        "user_role": current_user.user_role
    }

@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(UserProfile).all()

    return [
        {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "email": user.email,
            "user_role": user.user_role
        }
        for user in users
    ]


@router.get("/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(
        UserProfile.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        "email": user.email,
        "user_role": user.user_role
    }


from fastapi import Header


@router.post("/logout")
def logout(
    current_user: UserProfile = Depends(get_current_user)
):
    return {
        "message": f"User {current_user.username} logged out successfully"
    }


@router.post("/refresh")
def refresh_token(
    current_user: UserProfile = Depends(get_current_user)
):
    new_token = create_access_token({"sub": current_user.username})

    return {
        "access_token": new_token,
        "token_type": "bearer"
    }


