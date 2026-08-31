import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Ownership(Base):
    __tablename__ = "ownerships"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    variant_id = Column(String(36), ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True, index=True)
    purchase_date = Column(Date, nullable=False)
    purchase_price = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), nullable=True, default="INR")
    purchase_country = Column(String(100), nullable=True, default="India")
    ownership_start_date = Column(Date, nullable=False)
    ownership_end_date = Column(Date, nullable=True)
    status = Column(String(50), nullable=False, default="CURRENTLY_OWNING") # CURRENTLY_OWNING, PREVIOUSLY_OWNED
    previous_phone = Column(String(150), nullable=True)
    purchase_source = Column(String(100), nullable=True) # Official Store, Online Retailer, Offline Store, Second Hand
    owner_session_hash = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="ownerships")
    variant = relationship("ProductVariant", back_populates="ownerships")
    reports = relationship("ExperienceReport", back_populates="ownership", cascade="all, delete-orphan", order_by="ExperienceReport.ownership_duration_months")
