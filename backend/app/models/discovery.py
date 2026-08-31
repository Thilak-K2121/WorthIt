import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, Text
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class ProductDiscoveryRun(Base):
    __tablename__ = "product_discovery_runs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), nullable=False, default="RUNNING") # RUNNING, COMPLETED, FAILED
    sources_searched = Column(Integer, default=0, nullable=False)
    candidates_found = Column(Integer, default=0, nullable=False)
    extracted_count = Column(Integer, default=0, nullable=False)
    duplicates_detected = Column(Integer, default=0, nullable=False)
    new_products_created = Column(Integer, default=0, nullable=False)
    failed_count = Column(Integer, default=0, nullable=False)
    error_log = Column(Text, nullable=True)

    # Relationships
    sources = relationship("ProductSource", back_populates="discovery_run")
