import datetime
from decimal import Decimal
import random
from app.core.database import SessionLocal, Base, engine
from app.models.product import Product, ProductVariant, ProductSource
from app.models.ownership import Ownership
from app.models.experience import ExperienceReport
from app.models.issue import IssueCategory, ReportedIssue, RepairRecord
from app.models.discovery import ProductDiscoveryRun
from app.services.deduplication_service import DeduplicationService
from app.core.logging import logger

def seed_database():
    logger.info("Seeding realistic longitudinal dataset...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing data safely
    db.query(RepairRecord).delete()
    db.query(ReportedIssue).delete()
    db.query(ExperienceReport).delete()
    db.query(Ownership).delete()
    db.query(ProductVariant).delete()
    db.query(ProductSource).delete()
    db.query(Product).delete()
    db.query(ProductDiscoveryRun).delete()
    db.commit()

    # Ensure categories
    categories = {
        "battery": "Battery Degradation & Life",
        "heating": "Thermal / Heating",
        "display": "Display & Touch",
        "camera": "Camera & Optics",
        "charging": "Charging & Port",
        "software": "Software & UI Bugs",
        "performance": "Performance Degradation",
        "connectivity": "Connectivity & Network",
        "build": "Build & Physical Durability",
        "speaker_mic": "Speaker & Microphone"
    }
    cat_objs = {}
    for slug, name in categories.items():
        cat = db.query(IssueCategory).filter(IssueCategory.slug == slug).first()
        if not cat:
            cat = IssueCategory(slug=slug, display_name=name)
            db.add(cat)
            db.flush()
        cat_objs[slug] = cat
    db.commit()

    # 1. Google Pixel 8 Pro
    pixel = Product(
        brand="Google",
        model_name="Pixel 8 Pro",
        normalized_name="google-pixel-8-pro",
        official_name="Google Pixel 8 Pro",
        release_date=datetime.date(2023, 10, 12),
        country_market="Global",
        official_url="https://store.google.com/product/pixel_8_pro",
        status="ACTIVE",
        discovery_source="MANUAL",
        verification_status="VERIFIED",
        description="Google's flagship phone powered by the Tensor G3 with 7 years of promised software updates and pro camera controls."
    )
    db.add(pixel)
    db.flush()

    v_pixel1 = ProductVariant(product_id=pixel.id, ram="12GB", storage="128GB", chipset="Google Tensor G3", launch_price=Decimal("106999.00"), currency="INR")
    v_pixel2 = ProductVariant(product_id=pixel.id, ram="12GB", storage="256GB", chipset="Google Tensor G3", launch_price=Decimal("113999.00"), currency="INR")
    db.add_all([v_pixel1, v_pixel2])

    # 2. Samsung Galaxy S23 Ultra
    s23 = Product(
        brand="Samsung",
        model_name="Galaxy S23 Ultra",
        normalized_name="samsung-galaxy-s23-ultra",
        official_name="Samsung Galaxy S23 Ultra 5G",
        release_date=datetime.date(2023, 2, 17),
        country_market="Global",
        official_url="https://www.samsung.com/galaxy-s23-ultra",
        status="ACTIVE",
        discovery_source="MANUAL",
        verification_status="VERIFIED",
        description="Flagship powerhouse with Snapdragon 8 Gen 2 for Galaxy, 200MP main sensor, 10x optical periscope, and integrated S-Pen."
    )
    db.add(s23)
    db.flush()

    v_s23_1 = ProductVariant(product_id=s23.id, ram="12GB", storage="256GB", chipset="Snapdragon 8 Gen 2", launch_price=Decimal("124999.00"), currency="INR")
    v_s23_2 = ProductVariant(product_id=s23.id, ram="12GB", storage="512GB", chipset="Snapdragon 8 Gen 2", launch_price=Decimal("134999.00"), currency="INR")
    db.add_all([v_s23_1, v_s23_2])

    # 3. Apple iPhone 15 Pro
    iphone = Product(
        brand="Apple",
        model_name="iPhone 15 Pro",
        normalized_name="apple-iphone-15-pro",
        official_name="Apple iPhone 15 Pro",
        release_date=datetime.date(2023, 9, 22),
        country_market="Global",
        official_url="https://www.apple.com/iphone-15-pro",
        status="ACTIVE",
        discovery_source="MANUAL",
        verification_status="VERIFIED",
        description="Grade 5 titanium chassis, A17 Pro 3nm chip, customizable Action Button, and USB-C 3.0 data transfer speeds."
    )
    db.add(iphone)
    db.flush()

    v_ip1 = ProductVariant(product_id=iphone.id, ram="8GB", storage="128GB", chipset="Apple A17 Pro", launch_price=Decimal("134900.00"), currency="INR")
    v_ip2 = ProductVariant(product_id=iphone.id, ram="8GB", storage="256GB", chipset="Apple A17 Pro", launch_price=Decimal("144900.00"), currency="INR")
    db.add_all([v_ip1, v_ip2])

    # 4. OnePlus 12
    op12 = Product(
        brand="OnePlus",
        model_name="12",
        normalized_name="oneplus-12",
        official_name="OnePlus 12 5G",
        release_date=datetime.date(2024, 1, 23),
        country_market="Global",
        official_url="https://www.oneplus.com/12",
        status="ACTIVE",
        discovery_source="MANUAL",
        verification_status="VERIFIED",
        description="Equipped with Snapdragon 8 Gen 3, 5400mAh battery, 100W SuperVOOC, and 4th Gen Hasselblad Camera system."
    )
    db.add(op12)
    db.flush()

    v_op1 = ProductVariant(product_id=op12.id, ram="12GB", storage="256GB", chipset="Snapdragon 8 Gen 3", launch_price=Decimal("64999.00"), currency="INR")
    v_op2 = ProductVariant(product_id=op12.id, ram="16GB", storage="512GB", chipset="Snapdragon 8 Gen 3", launch_price=Decimal("69999.00"), currency="INR")
    db.add_all([v_op1, v_op2])

    # 5. Nothing Phone (2)
    nothing2 = Product(
        brand="Nothing",
        model_name="Phone (2)",
        normalized_name="nothing-phone-2",
        official_name="Nothing Phone (2)",
        release_date=datetime.date(2023, 7, 17),
        country_market="Global",
        official_url="https://nothing.tech/products/phone-2",
        status="ACTIVE",
        discovery_source="MANUAL",
        verification_status="VERIFIED",
        description="Unique Glyph interface with 33 addressable zones, Snapdragon 8+ Gen 1, and clean Nothing OS 2.5."
    )
    db.add(nothing2)
    db.flush()

    v_n1 = ProductVariant(product_id=nothing2.id, ram="8GB", storage="128GB", chipset="Snapdragon 8+ Gen 1", launch_price=Decimal("44999.00"), currency="INR")
    v_n2 = ProductVariant(product_id=nothing2.id, ram="12GB", storage="256GB", chipset="Snapdragon 8+ Gen 1", launch_price=Decimal("49999.00"), currency="INR")
    db.add_all([v_n1, v_n2])

    # 6. Motorola Edge 50 Ultra
    moto_edge = Product(
        brand="Motorola",
        model_name="Edge 50 Ultra",
        normalized_name="motorola-edge-50-ultra",
        official_name="Motorola Edge 50 Ultra",
        release_date=datetime.date(2024, 4, 16),
        country_market="Global",
        official_url="https://www.motorola.com/edge-50-ultra",
        status="ACTIVE",
        discovery_source="MANUAL",
        verification_status="VERIFIED",
        description="Real wood and vegan leather finish, Snapdragon 8s Gen 3, 144Hz pOLED display, and 125W TurboPower charging."
    )
    db.add(moto_edge)
    db.flush()

    v_moto = ProductVariant(product_id=moto_edge.id, ram="16GB", storage="512GB", chipset="Snapdragon 8s Gen 3", launch_price=Decimal("59999.00"), currency="INR")
    db.add(v_moto)
    db.flush()

    db.commit()

    # Generate longitudinal owner journeys
    # Pixel 8 Pro: 35 owners, mixed long-term sentiment on battery/modem, high camera praise
    for i in range(1, 36):
        purchase_m = random.randint(14, 22)
        p_date = datetime.date.today() - datetime.timedelta(days=purchase_m * 30)
        owner = Ownership(
            product_id=pixel.id,
            variant_id=v_pixel1.id if i % 2 == 0 else v_pixel2.id,
            purchase_date=p_date,
            purchase_price=Decimal(str(random.choice([99999, 106999, 89999]))),
            ownership_start_date=p_date,
            status="CURRENTLY_OWNING",
            purchase_source=random.choice(["Flipkart", "Official Google Store", "Reliance Digital"]),
            previous_phone=random.choice(["Pixel 6", "iPhone 11", "OnePlus 9 Pro", "Galaxy S21"])
        )
        db.add(owner)
        db.flush()

        # Multi-report timeline for each owner (e.g. 3m, 6m, 12m, 18m)
        durations = [3, 6, 12] if purchase_m >= 12 else [3, 6]
        if purchase_m >= 18:
            durations.append(18)

        for d in durations:
            # Over time, satisfaction changes slightly
            sat_drop = 0.3 if d >= 12 else 0.0
            r = ExperienceReport(
                ownership_id=owner.id,
                report_date=p_date + datetime.timedelta(days=d * 30),
                ownership_duration_months=d,
                report_version=durations.index(d) + 1,
                overall_satisfaction=Decimal(str(round(max(3.2, 4.5 - sat_drop + random.uniform(-0.3, 0.3)), 1))),
                battery_satisfaction=Decimal(str(round(max(2.8, 4.0 - (sat_drop * 1.5) + random.uniform(-0.3, 0.3)), 1))),
                performance_satisfaction=Decimal(str(round(min(5.0, 4.4 + random.uniform(-0.2, 0.4)), 1))),
                software_satisfaction=Decimal(str(round(min(5.0, 4.8 + random.uniform(-0.2, 0.2)), 1))),
                camera_satisfaction=Decimal("4.9"),
                build_satisfaction=Decimal("4.5"),
                battery_degradation_perception="MODERATE" if d >= 12 else ("MINOR" if d == 6 else "NONE"),
                heating_experience="NOTICEABLE_WARMTH" if d >= 6 else "NORMAL",
                software_update_experience="EXCELLENT",
                would_buy_again="YES" if random.random() > 0.18 else ("UNSURE" if random.random() > 0.5 else "NO"),
                would_buy_again_reason="Camera quality and stock Android software are unrivaled, though battery on 5G could be better." if d >= 12 else "Incredible photo processing.",
                biggest_positive="Pro camera features, natural skin tones, and regular Feature Drops.",
                biggest_problem="Modem heats up slightly and drains battery during prolonged cellular video streaming.",
                trust_status="SELF_REPORTED"
            )
            db.add(r)
            db.flush()

            # Add structured issue if at 12m or 18m
            if d == 12 and i % 3 == 0:
                iss = ReportedIssue(
                    experience_report_id=r.id,
                    category_id=cat_objs["battery"].id,
                    issue_title="Battery health dropped to ~86% after 1 year of fast charging",
                    severity="MODERATE",
                    occurred_at_month=11,
                    resolved=False,
                    repair_required=False
                )
                db.add(iss)

    # Samsung Galaxy S23 Ultra: 45 owners, very high satisfaction, great endurance, occasional green line / screen repairs
    for i in range(1, 46):
        purchase_m = random.randint(16, 26)
        p_date = datetime.date.today() - datetime.timedelta(days=purchase_m * 30)
        owner = Ownership(
            product_id=s23.id,
            variant_id=v_s23_1.id if i % 2 == 0 else v_s23_2.id,
            purchase_date=p_date,
            purchase_price=Decimal(str(random.choice([114999, 124999, 99999]))),
            ownership_start_date=p_date,
            status="CURRENTLY_OWNING",
            purchase_source="Samsung Official Store",
            previous_phone=random.choice(["Note 20 Ultra", "S21 Ultra", "iPhone 13 Pro"])
        )
        db.add(owner)
        db.flush()

        durations = [3, 6, 12, 18] if purchase_m >= 18 else [3, 6, 12]
        for d in durations:
            r = ExperienceReport(
                ownership_id=owner.id,
                report_date=p_date + datetime.timedelta(days=d * 30),
                ownership_duration_months=d,
                report_version=durations.index(d) + 1,
                overall_satisfaction=Decimal(str(round(min(5.0, 4.7 + random.uniform(-0.3, 0.3)), 1))),
                battery_satisfaction=Decimal(str(round(min(5.0, 4.6 + random.uniform(-0.3, 0.3)), 1))),
                performance_satisfaction=Decimal(str(round(min(5.0, 4.8 + random.uniform(-0.2, 0.2)), 1))),
                software_satisfaction=Decimal(str(round(min(5.0, 4.5 + random.uniform(-0.3, 0.3)), 1))),
                camera_satisfaction=Decimal("4.8"),
                build_satisfaction=Decimal("4.9"),
                battery_degradation_perception="MINOR" if d >= 18 else "NONE",
                heating_experience="COOL",
                software_update_experience="GOOD",
                would_buy_again="YES" if random.random() > 0.08 else "UNSURE",
                would_buy_again_reason="Snapdragon 8 Gen 2 efficiency is rock solid. Outstanding battery even after 1.5 years.",
                biggest_positive="Zoom camera up to 30x is crystal clear, battery routinely gives 8+ hours screen-on-time.",
                biggest_problem="Heavy and bulky in pocket with sharp corners.",
                trust_status="SELF_REPORTED"
            )
            db.add(r)
            db.flush()

            if d == 18 and i % 8 == 0:
                # Add display repair record
                rep = RepairRecord(
                    experience_report_id=r.id,
                    part_replaced="SCREEN",
                    official_service_center=True,
                    covered_under_warranty=False,
                    cost=Decimal("18500.00"),
                    currency="INR",
                    repair_notes="Replaced OLED assembly due to small vertical line after an update."
                )
                db.add(rep)

    # OnePlus 12: 30 owners, rapid charging praised, outstanding value
    for i in range(1, 31):
        purchase_m = random.randint(6, 14)
        p_date = datetime.date.today() - datetime.timedelta(days=purchase_m * 30)
        owner = Ownership(
            product_id=op12.id,
            variant_id=v_op1.id if i % 2 == 0 else v_op2.id,
            purchase_date=p_date,
            purchase_price=Decimal("64999.00"),
            ownership_start_date=p_date,
            status="CURRENTLY_OWNING",
            purchase_source="Amazon",
            previous_phone="OnePlus 8T"
        )
        db.add(owner)
        db.flush()

        durations = [3, 6, 12] if purchase_m >= 12 else [3, 6]
        for d in durations:
            r = ExperienceReport(
                ownership_id=owner.id,
                report_date=p_date + datetime.timedelta(days=d * 30),
                ownership_duration_months=d,
                report_version=durations.index(d) + 1,
                overall_satisfaction=Decimal(str(round(min(5.0, 4.6 + random.uniform(-0.3, 0.3)), 1))),
                battery_satisfaction=Decimal("4.8"),
                performance_satisfaction=Decimal("4.9"),
                software_satisfaction=Decimal("4.2"),
                camera_satisfaction=Decimal("4.4"),
                build_satisfaction=Decimal("4.6"),
                battery_degradation_perception="NONE",
                heating_experience="COOL",
                software_update_experience="GOOD",
                would_buy_again="YES" if random.random() > 0.10 else "UNSURE",
                would_buy_again_reason="100W charging is life changing. 0 to 100% in 26 minutes.",
                biggest_positive="Super fast charging and silky smooth 120Hz display.",
                biggest_problem="Curved screen makes finding good tempered glass protectors difficult.",
                trust_status="SELF_REPORTED"
            )
            db.add(r)

    # Seed an automated discovery run log
    run = ProductDiscoveryRun(
        status="COMPLETED",
        started_at=datetime.datetime.utcnow() - datetime.timedelta(hours=6),
        completed_at=datetime.datetime.utcnow() - datetime.timedelta(hours=5, minutes=58),
        sources_searched=8,
        candidates_found=12,
        extracted_count=10,
        duplicates_detected=7,
        new_products_created=3,
        failed_count=0
    )
    db.add(run)

    db.commit()
    db.close()
    logger.info("Successfully seeded smartphone catalog and longitudinal ownership records.")

if __name__ == "__main__":
    seed_database()
