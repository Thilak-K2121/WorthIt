import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ProductSuggestion(Base):
    __tablename__ = "product_suggestions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand = Column(String(100), nullable=False)
    model_name = Column(String(150), nullable=False)
    variant_details = Column(String(255), nullable=True) # e.g. "12GB / 256GB"
    official_url = Column(String(500), nullable=True)
    approximate_release_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="PENDING") # PENDING, APPROVED, REJECTED, DUPLICATE
    target_product_id = Column(String(36), ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    submitter_ip_hash = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    target_product = relationship("Product")
