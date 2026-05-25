from pydantic import BaseModel
from typing import Optional


# =========================
# LOGIN SCHEMA
# =========================
class Login(BaseModel):
    email: str
    password: str


# =========================
# ADMIN CREATE SCHEMA
# =========================
class AdminCreate(BaseModel):
    name: str
    email: str
    password: str


# =========================
# USER REGISTRATION
# =========================
class UserCreate(BaseModel):
    name: str
    age: int
    mobile: str
    address: str
    district: str
    state: str
    health_problem: Optional[str] = None


# =========================
# REVIEW SCHEMA
# =========================
class ReviewCreate(BaseModel):
    name: str
    city: str
    rating: int
    health_improvement: str
    message: str


# =========================
# BRANCH SCHEMA
# =========================
class BranchCreate(BaseModel):
    name: str
    address: str
    batch_time: str
    trainer: str
    contact: str
    map_link: str


# =========================
# GALLERY SCHEMA
# =========================
class GalleryCreate(BaseModel):
    image: str