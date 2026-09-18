from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.security import MAX_PASSWORD_BYTES


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    is_staff: bool


class SignupIn(BaseModel):
    username: str = Field(min_length=3, max_length=150)
    email: EmailStr
    password1: str = Field(min_length=8, max_length=MAX_PASSWORD_BYTES)
    password2: str = Field(min_length=8, max_length=MAX_PASSWORD_BYTES)


class LoginIn(BaseModel):
    username: str
    password: str


class AuthOut(BaseModel):
    """Signup and login both answer this: the token, and enough to draw the header."""

    token: str
    user: UserOut
