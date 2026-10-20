from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Literal


class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: EmailStr
    user_role: Literal["simple_user", "courier", "store_owner"] = "simple_user"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    user_role: str

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    email: EmailStr | None = None
    user_role: Literal["simple_user", "courier", "store_owner"] | None = None
