import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Numeric, Text, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    brand = Column(String(100), nullable=False, index=True)
    model_name = Column(String(150), nullable=False)
    normalized_name = Column(String(200), nullable=False, unique=True, index=True)
    official_name = Column(String(200), nullable=True)
    release_date = Column(Date, nullable=True)
    country_market = Column(String(100), nullable=True, default="Global")
    official_url = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="ACTIVE") # ACTIVE, PENDING, DISCONTINUED
    discovery_source = Column(String(50), nullable=False, default="MANUAL") # MANUAL, AUTOMATED, USER_SUGGESTED
    verification_status = Column(String(50), nullable=False, default="VERIFIED") # VERIFIED, UNVERIFIED, FLAGGED
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    variants = relationship("ProductVariant", back_populates="product", cascade="all, delete-orphan")
    sources = relationship("ProductSource", back_populates="product", cascade="all, delete-orphan")
    ownerships = relationship("Ownership", back_populates="product", cascade="all, delete-orphan")

class ProductVariant(Base):
    __tablename__ = "product_variants"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True)
    ram = Column(String(50), nullable=True) # e.g. "12GB"
    storage = Column(String(50), nullable=True) # e.g. "256GB"
    chipset = Column(String(150), nullable=True) # e.g. "Snapdragon 8 Gen 3"
    launch_price = Column(Numeric(12, 2), nullable=True)
    currency = Column(String(10), nullable=True, default="INR")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="variants")
    ownerships = relationship("Ownership", back_populates="variant")

class ProductSource(Base):
    __tablename__ = "product_sources"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    product_id = Column(String(36), ForeignKey("products.id", ondelete="CASCADE"), nullable=True, index=True)
    discovery_run_id = Column(String(36), ForeignKey("product_discovery_runs.id", ondelete="SET NULL"), nullable=True, index=True)
    source_url = Column(String(1000), nullable=False)
    source_title = Column(String(500), nullable=True)
    source_snippet = Column(Text, nullable=True)
    provider = Column(String(50), nullable=False, default="TAVILY") # TAVILY, MANUAL_SUBMISSION, RSS
    raw_extracted_json = Column(JSON, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    product = relationship("Product", back_populates="sources")
    discovery_run = relationship("ProductDiscoveryRun", back_populates="sources")

    @property
    def product_name(self):
        return f"{self.product.brand} {self.product.model_name}" if self.product else None

    @property
    def brand(self):
        return self.product.brand if self.product else None

    @property
    def model_name(self):
        return self.product.model_name if self.product else None
