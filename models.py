from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from database import Base


# =========================
# ADMIN TABLE
# =========================
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password = Column(String)
    role = Column(String(20))
    is_approved = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)


# =========================
# USERS TABLE
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    age = Column(Integer)
    mobile = Column(String(10))
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    health_problem = Column(Text, nullable=True)


# =========================
# REVIEWS TABLE
# =========================
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    city = Column(String(100))
    rating = Column(Integer)
    health_improvement = Column(String(255))
    message = Column(Text)
    photo = Column(String(255), nullable=True)


# =========================
# BRANCHES TABLE
# =========================
class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(Text)
    batch_time = Column(String(100))
    trainer = Column(String(100))
    contact = Column(String(20))
    map_link = Column(Text)


# =========================
# GALLERY TABLE
# =========================
class Gallery(Base):
    __tablename__ = "gallery"

    id = Column(Integer, primary_key=True, index=True)
    image = Column(String(255))