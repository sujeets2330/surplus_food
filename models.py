from datetime import datetime
from sqlalchemy import (
    create_engine, String, Integer, Boolean, DateTime, Float, ForeignKey, Text, Column
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from config import Config

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    # Email as primary key per requirements
    email = Column(String(255), primary_key=True)
    name = Column(String(120), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, default="")
    pincode = Column(String(10), default="")
    role = Column(String(20), nullable=False)  # donor / recipient / admin
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    donations = relationship(
        "FoodDonation", back_populates="donor", cascade="all, delete-orphan"
    )
    requests = relationship(
        "FoodRequest", back_populates="recipient", cascade="all, delete-orphan"
    )

class FoodDonation(Base):
    __tablename__ = "food_donations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    donor_email = Column(String(255), ForeignKey("users.email"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    is_veg = Column(Boolean, default=True)
    quantity_meals = Column(Integer, default=1)
    ready_by = Column(DateTime, nullable=False)
    expire_by = Column(DateTime, nullable=False)

    address = Column(Text, nullable=False)
    pincode = Column(String(10), nullable=False)
    lat = Column(Float, default=0.0)
    lon = Column(Float, default=0.0)

    status = Column(String(30), default="open")  # open, matched, picked, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("User", back_populates="donations")
    match = relationship("Match", back_populates="donation", uselist=False)

class FoodRequest(Base):
    __tablename__ = "food_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    recipient_email = Column(String(255), ForeignKey("users.email"), nullable=False)
    need_meals = Column(Integer, default=1)
    prefers_veg = Column(Boolean, default=True)
    earliest = Column(DateTime, nullable=False)
    latest = Column(DateTime, nullable=False)
    address = Column(Text, nullable=False)
    pincode = Column(String(10), nullable=False)
    lat = Column(Float, default=0.0)
    lon = Column(Float, default=0.0)
    status = Column(String(30), default="open")  # open, matched, fulfilled, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    recipient = relationship("User", back_populates="requests")
    match = relationship("Match", back_populates="request", uselist=False)

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    capacity_meals = Column(Integer, default=50)
    base_lat = Column(Float, default=0.0)
    base_lon = Column(Float, default=0.0)
    is_available = Column(Boolean, default=True)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    donation_id = Column(Integer, ForeignKey("food_donations.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("food_requests.id"), nullable=False)
    score = Column(Float, default=0.0)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"), nullable=True)
    route_json = Column(Text, nullable=True)

    status = Column(String(30), default="planned")  # planned, assigned, enroute, delivered, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)

    donation = relationship("FoodDonation", back_populates="match")
    request = relationship("FoodRequest", back_populates="match")
    vehicle = relationship("Vehicle")

def init_db():
    Base.metadata.create_all(bind=engine)
