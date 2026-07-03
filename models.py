from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class Bike(Base):
    """Royal Enfield Motorcycle Model"""
    __tablename__ = "bikes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    model_code = Column(String(50), unique=True, nullable=False)
    category = Column(String(50), nullable=False)  # e.g., Classic, Himalayan, Bullet, Meteor
    variant = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    price_inr = Column(Float, nullable=False)

    # Engine Specs
    engine_cc = Column(Integer, nullable=True)
    engine_type = Column(String(100), nullable=True)
    max_power_bhp = Column(Float, nullable=True)
    max_torque_nm = Column(Float, nullable=True)
    transmission = Column(String(50), nullable=True)

    # Dimensions
    weight_kg = Column(Float, nullable=True)
    fuel_tank_litres = Column(Float, nullable=True)
    seat_height_mm = Column(Integer, nullable=True)

    # Meta
    is_available = Column(Boolean, default=True)
    year_launched = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Dealer(Base):
    """Authorized Royal Enfield Dealer"""
    __tablename__ = "dealers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    address = Column(Text, nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    """
    Royal Enfield Customer Booking — single-row lifecycle model.

    One row per booking_id. Kissflow sends partial payloads at each
    phase; the API inserts on first call and patches only the provided
    fields on every subsequent call.

    Phases
    ──────
    1. Initial Booking  → booking_id, customer_name, email, city,
                          interested_model, finance_required
    2. Finance          → preferred_bank, loan_amount, loan_status
    3. Vehicle Alloc.   → vehicle_available, chassis_number, engine_number
    4. Delivery         → delivery_status, registration_status,
                          insurance_status
    """
    __tablename__ = "bookings"

    # ── Identity ─────────────────────────────────────────────────────
    booking_id       = Column(String(50),  primary_key=True, index=True)

    # ── Phase 1 : Initial Booking ─────────────────────────────────────
    customer_name    = Column(String(150), nullable=True)
    email            = Column(String(150), nullable=True)
    city             = Column(String(100), nullable=True)
    interested_model = Column(String(100), nullable=True)
    finance_required = Column(String(10),  nullable=True)   # "Yes" / "No"

    # ── Phase 2 : Finance ─────────────────────────────────────────────
    preferred_bank   = Column(String(100), nullable=True)
    loan_amount      = Column(Float,       nullable=True)
    loan_status      = Column(String(50),  nullable=True)   # Approved / Rejected / Pending

    # ── Phase 3 : Vehicle Allocation ──────────────────────────────────
    vehicle_available = Column(String(10),  nullable=True)  # "Yes" / "No"
    chassis_number    = Column(String(100), nullable=True)
    engine_number     = Column(String(100), nullable=True)

    # ── Phase 4 : Delivery ────────────────────────────────────────────
    delivery_status     = Column(String(50), nullable=True)
    registration_status = Column(String(50), nullable=True)
    insurance_status    = Column(String(50), nullable=True)

    # ── Timestamps ────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
