from app.services.deduplication_service import DeduplicationService
from app.models.product import Product

def test_brand_normalization():
    assert DeduplicationService.normalize_brand("samsung") == "Samsung"
    assert DeduplicationService.normalize_brand("apple inc") == "Apple"
    assert DeduplicationService.normalize_brand("one plus") == "OnePlus"
    assert DeduplicationService.normalize_brand("1+") == "OnePlus"
    assert DeduplicationService.normalize_brand("mi") == "Xiaomi"
    assert DeduplicationService.normalize_brand("nothing tech") == "Nothing"

def test_normalized_key_generation():
    assert DeduplicationService.generate_normalized_key("Samsung", "Galaxy S26 Ultra 5G") == "samsung-galaxy-s26-ultra"
    assert DeduplicationService.generate_normalized_key("Apple", "iPhone 15 Pro Max (Global Edition)") == "apple-iphone-15-pro-max"
    assert DeduplicationService.generate_normalized_key("Xiaomi", "Xiaomi 14 Ultra Dual SIM") == "xiaomi-14-ultra"

def test_find_existing_duplicate_exact_and_fuzzy(db_session):
    p = Product(
        brand="Samsung",
        model_name="Galaxy S24 Ultra",
        normalized_name="samsung-galaxy-s24-ultra",
        status="ACTIVE",
        verification_status="VERIFIED"
    )
    db_session.add(p)
    db_session.commit()

    # Exact match check
    match, score = DeduplicationService.find_existing_duplicate(db_session, "Samsung", "Galaxy S24 Ultra 5G")
    assert match is not None
    assert match.id == p.id
    assert score == 1.0

    # Token match check
    match2, score2 = DeduplicationService.find_existing_duplicate(db_session, "Samsung", "S24 Ultra Galaxy")
    assert match2 is not None
    assert match2.id == p.id
    assert score2 >= 0.8
