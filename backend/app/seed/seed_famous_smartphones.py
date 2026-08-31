import sys
import uuid
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.models.product import Product, ProductVariant
from app.core.logging import logger
from app.services.deduplication_service import DeduplicationService

SMARTPHONES_DATA = [
    # --- APPLE ---
    {"brand": "Apple", "model_name": "iPhone 16 Pro Max", "release_date": "2024-09-20", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Apple A18 Pro", "price": 144900},
        {"ram": "8GB", "storage": "512GB", "chipset": "Apple A18 Pro", "price": 164900},
        {"ram": "8GB", "storage": "1TB", "chipset": "Apple A18 Pro", "price": 184900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 16 Pro", "release_date": "2024-09-20", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Apple A18 Pro", "price": 119900},
        {"ram": "8GB", "storage": "256GB", "chipset": "Apple A18 Pro", "price": 129900},
        {"ram": "8GB", "storage": "512GB", "chipset": "Apple A18 Pro", "price": 149900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 16 Plus", "release_date": "2024-09-20", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Apple A18", "price": 89900},
        {"ram": "8GB", "storage": "256GB", "chipset": "Apple A18", "price": 99900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 16", "release_date": "2024-09-20", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Apple A18", "price": 79900},
        {"ram": "8GB", "storage": "256GB", "chipset": "Apple A18", "price": 89900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 15 Pro Max", "release_date": "2023-09-22", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Apple A17 Pro", "price": 159900},
        {"ram": "8GB", "storage": "512GB", "chipset": "Apple A17 Pro", "price": 179900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 15 Pro", "release_date": "2023-09-22", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Apple A17 Pro", "price": 134900},
        {"ram": "8GB", "storage": "256GB", "chipset": "Apple A17 Pro", "price": 144900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 15 Plus", "release_date": "2023-09-22", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "Apple A16 Bionic", "price": 89900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 15", "release_date": "2023-09-22", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "Apple A16 Bionic", "price": 79900},
        {"ram": "6GB", "storage": "256GB", "chipset": "Apple A16 Bionic", "price": 89900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 14 Pro Max", "release_date": "2022-09-16", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "Apple A16 Bionic", "price": 139900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 14", "release_date": "2022-09-16", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "Apple A15 Bionic", "price": 69900},
    ]},
    {"brand": "Apple", "model_name": "iPhone 13", "release_date": "2021-09-24", "variants": [
        {"ram": "4GB", "storage": "128GB", "chipset": "Apple A15 Bionic", "price": 59900},
    ]},

    # --- SAMSUNG ---
    {"brand": "Samsung", "model_name": "Galaxy S24 Ultra", "release_date": "2024-01-24", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3 for Galaxy", "price": 129999},
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3 for Galaxy", "price": 139999},
        {"ram": "12GB", "storage": "1TB", "chipset": "Snapdragon 8 Gen 3 for Galaxy", "price": 159999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy S24 Plus", "release_date": "2024-01-24", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Exynos 2400", "price": 99999},
        {"ram": "12GB", "storage": "512GB", "chipset": "Exynos 2400", "price": 109999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy S24", "release_date": "2024-01-24", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Exynos 2400", "price": 79999},
        {"ram": "8GB", "storage": "256GB", "chipset": "Exynos 2400", "price": 89999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy S23 Ultra", "release_date": "2023-02-17", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 2 for Galaxy", "price": 124999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy S23 FE", "release_date": "2023-10-05", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Exynos 2200", "price": 59999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy Z Fold 6", "release_date": "2024-07-24", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 164999},
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 176999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy Z Flip 6", "release_date": "2024-07-24", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 109999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy A55 5G", "release_date": "2024-03-15", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Exynos 1480", "price": 39999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Exynos 1480", "price": 45999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy A35 5G", "release_date": "2024-03-15", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Exynos 1380", "price": 30999},
    ]},
    {"brand": "Samsung", "model_name": "Galaxy M35 5G", "release_date": "2024-07-17", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "Exynos 1380", "price": 19999},
    ]},

    # --- GOOGLE PIXEL ---
    {"brand": "Google", "model_name": "Pixel 9 Pro XL", "release_date": "2024-08-22", "variants": [
        {"ram": "16GB", "storage": "256GB", "chipset": "Google Tensor G4", "price": 124999},
        {"ram": "16GB", "storage": "512GB", "chipset": "Google Tensor G4", "price": 139999},
    ]},
    {"brand": "Google", "model_name": "Pixel 9 Pro", "release_date": "2024-08-22", "variants": [
        {"ram": "16GB", "storage": "128GB", "chipset": "Google Tensor G4", "price": 109999},
    ]},
    {"brand": "Google", "model_name": "Pixel 9", "release_date": "2024-08-22", "variants": [
        {"ram": "12GB", "storage": "128GB", "chipset": "Google Tensor G4", "price": 79999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Google Tensor G4", "price": 89999},
    ]},
    {"brand": "Google", "model_name": "Pixel 9 Pro Fold", "release_date": "2024-09-04", "variants": [
        {"ram": "16GB", "storage": "256GB", "chipset": "Google Tensor G4", "price": 172999},
    ]},
    {"brand": "Google", "model_name": "Pixel 8 Pro", "release_date": "2023-10-12", "variants": [
        {"ram": "12GB", "storage": "128GB", "chipset": "Google Tensor G3", "price": 106999},
    ]},
    {"brand": "Google", "model_name": "Pixel 8", "release_date": "2023-10-12", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Google Tensor G3", "price": 75999},
    ]},
    {"brand": "Google", "model_name": "Pixel 8a", "release_date": "2024-05-14", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Google Tensor G3", "price": 52999},
    ]},
    {"brand": "Google", "model_name": "Pixel 7a", "release_date": "2023-05-10", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Google Tensor G2", "price": 43999},
    ]},

    # --- ONEPLUS ---
    {"brand": "OnePlus", "model_name": "OnePlus 12", "release_date": "2024-01-23", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 64999},
        {"ram": "16GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 69999},
    ]},
    {"brand": "OnePlus", "model_name": "OnePlus 12R", "release_date": "2024-01-23", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 8 Gen 2", "price": 39999},
        {"ram": "16GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 2", "price": 45999},
    ]},
    {"brand": "OnePlus", "model_name": "OnePlus Open", "release_date": "2023-10-19", "variants": [
        {"ram": "16GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 2", "price": 139999},
    ]},
    {"brand": "OnePlus", "model_name": "OnePlus 11 5G", "release_date": "2023-02-07", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 8 Gen 2", "price": 56999},
    ]},
    {"brand": "OnePlus", "model_name": "OnePlus Nord 4", "release_date": "2024-07-16", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7+ Gen 3", "price": 29999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 7+ Gen 3", "price": 32999},
    ]},
    {"brand": "OnePlus", "model_name": "OnePlus Nord CE 4", "release_date": "2024-04-01", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7 Gen 3", "price": 24999},
    ]},
    {"brand": "OnePlus", "model_name": "OnePlus Nord CE 4 Lite", "release_date": "2024-06-24", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 695", "price": 19999},
    ]},

    # --- VIVO ---
    {"brand": "Vivo", "model_name": "Vivo X100 Pro", "release_date": "2024-01-04", "variants": [
        {"ram": "16GB", "storage": "512GB", "chipset": "MediaTek Dimensity 9300", "price": 89999},
    ]},
    {"brand": "Vivo", "model_name": "Vivo X100", "release_date": "2024-01-04", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "MediaTek Dimensity 9300", "price": 63999},
    ]},
    {"brand": "Vivo", "model_name": "Vivo V40 Pro", "release_date": "2024-08-07", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 9200+", "price": 49999},
        {"ram": "12GB", "storage": "512GB", "chipset": "MediaTek Dimensity 9200+", "price": 55999},
    ]},
    {"brand": "Vivo", "model_name": "Vivo V40", "release_date": "2024-08-07", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7 Gen 3", "price": 34999},
    ]},
    {"brand": "Vivo", "model_name": "Vivo T3 Pro 5G", "release_date": "2024-08-27", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7 Gen 3", "price": 24999},
    ]},
    {"brand": "Vivo", "model_name": "Vivo T3 5G", "release_date": "2024-03-21", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7200", "price": 19999},
    ]},

    # --- IQOO ---
    {"brand": "iQOO", "model_name": "iQOO 12 5G", "release_date": "2023-12-12", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 52999},
        {"ram": "16GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 57999},
    ]},
    {"brand": "iQOO", "model_name": "iQOO Neo 9 Pro", "release_date": "2024-02-22", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 8 Gen 2", "price": 35999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 2", "price": 37999},
    ]},
    {"brand": "iQOO", "model_name": "iQOO Z9s Pro 5G", "release_date": "2024-08-21", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7 Gen 3", "price": 24999},
    ]},
    {"brand": "iQOO", "model_name": "iQOO Z9 5G", "release_date": "2024-03-12", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7200", "price": 19999},
    ]},

    # --- XIAOMI & REDMI ---
    {"brand": "Xiaomi", "model_name": "Xiaomi 14 Ultra", "release_date": "2024-03-07", "variants": [
        {"ram": "16GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 99999},
    ]},
    {"brand": "Xiaomi", "model_name": "Xiaomi 14", "release_date": "2024-03-07", "variants": [
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 69999},
    ]},
    {"brand": "Xiaomi", "model_name": "Redmi Note 13 Pro+ 5G", "release_date": "2024-01-04", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 7200 Ultra", "price": 31999},
        {"ram": "12GB", "storage": "512GB", "chipset": "MediaTek Dimensity 7200 Ultra", "price": 35999},
    ]},
    {"brand": "Xiaomi", "model_name": "Redmi Note 13 Pro 5G", "release_date": "2024-01-04", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7s Gen 2", "price": 25999},
    ]},
    {"brand": "Xiaomi", "model_name": "Redmi Note 13 5G", "release_date": "2024-01-04", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "MediaTek Dimensity 6080", "price": 17999},
    ]},
    {"brand": "Xiaomi", "model_name": "Redmi 13C 5G", "release_date": "2023-12-06", "variants": [
        {"ram": "4GB", "storage": "128GB", "chipset": "MediaTek Dimensity 6100+", "price": 10999},
    ]},

    # --- POCO ---
    {"brand": "Poco", "model_name": "Poco F6 5G", "release_date": "2024-05-23", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Snapdragon 8s Gen 3", "price": 29999},
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8s Gen 3", "price": 33999},
    ]},
    {"brand": "Poco", "model_name": "Poco X6 Pro 5G", "release_date": "2024-01-11", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 8300 Ultra", "price": 26999},
        {"ram": "12GB", "storage": "512GB", "chipset": "MediaTek Dimensity 8300 Ultra", "price": 28999},
    ]},
    {"brand": "Poco", "model_name": "Poco X6 5G", "release_date": "2024-01-11", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Snapdragon 7s Gen 2", "price": 21999},
    ]},
    {"brand": "Poco", "model_name": "Poco M6 Pro 5G", "release_date": "2023-08-05", "variants": [
        {"ram": "4GB", "storage": "64GB", "chipset": "Snapdragon 4 Gen 2", "price": 10999},
    ]},

    # --- REALME ---
    {"brand": "Realme", "model_name": "Realme GT 6", "release_date": "2024-06-20", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Snapdragon 8s Gen 3", "price": 40999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8s Gen 3", "price": 42999},
    ]},
    {"brand": "Realme", "model_name": "Realme GT 6T", "release_date": "2024-05-22", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7+ Gen 3", "price": 30999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 7+ Gen 3", "price": 35999},
    ]},
    {"brand": "Realme", "model_name": "Realme 13 Pro+ 5G", "release_date": "2024-07-30", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Snapdragon 7s Gen 2", "price": 32999},
    ]},
    {"brand": "Realme", "model_name": "Realme 12 Pro+ 5G", "release_date": "2024-01-29", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7s Gen 2", "price": 29999},
    ]},
    {"brand": "Realme", "model_name": "Realme Narzo 70 Pro 5G", "release_date": "2024-03-19", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7050", "price": 19999},
    ]},
    {"brand": "Realme", "model_name": "Realme P1 Pro 5G", "release_date": "2024-04-15", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 6 Gen 1", "price": 21999},
    ]},

    # --- OPPO ---
    {"brand": "Oppo", "model_name": "Oppo Find X7 Ultra", "release_date": "2024-01-08", "variants": [
        {"ram": "16GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 89999},
    ]},
    {"brand": "Oppo", "model_name": "Oppo Find N3 Flip", "release_date": "2023-10-12", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "MediaTek Dimensity 9200", "price": 94999},
    ]},
    {"brand": "Oppo", "model_name": "Oppo Reno 12 Pro 5G", "release_date": "2024-07-12", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "MediaTek Dimensity 7300 Energy", "price": 36999},
    ]},
    {"brand": "Oppo", "model_name": "Oppo Reno 12 5G", "release_date": "2024-07-12", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 7300 Energy", "price": 32999},
    ]},
    {"brand": "Oppo", "model_name": "Oppo F27 Pro+ 5G", "release_date": "2024-06-13", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7050", "price": 27999},
    ]},

    # --- MOTOROLA ---
    {"brand": "Motorola", "model_name": "Motorola Razr 50 Ultra", "release_date": "2024-07-04", "variants": [
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8s Gen 3", "price": 99999},
    ]},
    {"brand": "Motorola", "model_name": "Motorola Edge 50 Ultra", "release_date": "2024-06-18", "variants": [
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8s Gen 3", "price": 59999},
    ]},
    {"brand": "Motorola", "model_name": "Motorola Edge 50 Pro", "release_date": "2024-04-03", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Snapdragon 7 Gen 3", "price": 31999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 7 Gen 3", "price": 35999},
    ]},
    {"brand": "Motorola", "model_name": "Motorola Edge 50 Fusion", "release_date": "2024-05-16", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 7s Gen 2", "price": 22999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 7s Gen 2", "price": 24999},
    ]},
    {"brand": "Motorola", "model_name": "Moto G85 5G", "release_date": "2024-07-10", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 6s Gen 3", "price": 17999},
    ]},
    {"brand": "Motorola", "model_name": "Moto G64 5G", "release_date": "2024-04-16", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7025", "price": 14999},
    ]},

    # --- NOTHING ---
    {"brand": "Nothing", "model_name": "Nothing Phone (2)", "release_date": "2023-07-11", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 8+ Gen 1", "price": 44999},
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8+ Gen 1", "price": 49999},
    ]},
    {"brand": "Nothing", "model_name": "Nothing Phone (2a) Plus", "release_date": "2024-07-31", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 7350 Pro", "price": 27999},
    ]},
    {"brand": "Nothing", "model_name": "Nothing Phone (2a)", "release_date": "2024-03-05", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7200 Pro", "price": 23999},
        {"ram": "12GB", "storage": "256GB", "chipset": "MediaTek Dimensity 7200 Pro", "price": 27999},
    ]},
    {"brand": "Nothing", "model_name": "CMF Phone 1", "release_date": "2024-07-08", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7300", "price": 15999},
        {"ram": "8GB", "storage": "128GB", "chipset": "MediaTek Dimensity 7300", "price": 17999},
    ]},

    # --- ASUS ---
    {"brand": "Asus", "model_name": "ROG Phone 8 Pro", "release_date": "2024-01-09", "variants": [
        {"ram": "16GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 94999},
        {"ram": "24GB", "storage": "1TB", "chipset": "Snapdragon 8 Gen 3", "price": 119999},
    ]},
    {"brand": "Asus", "model_name": "ROG Phone 8", "release_date": "2024-01-09", "variants": [
        {"ram": "16GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 79999},
    ]},
    {"brand": "Asus", "model_name": "Zenfone 11 Ultra", "release_date": "2024-03-14", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 74999},
    ]},
    {"brand": "Asus", "model_name": "Zenfone 10", "release_date": "2023-06-29", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 8 Gen 2", "price": 64999},
    ]},

    # --- SONY ---
    {"brand": "Sony", "model_name": "Xperia 1 VI", "release_date": "2024-05-15", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "Snapdragon 8 Gen 3", "price": 119999},
    ]},
    {"brand": "Sony", "model_name": "Xperia 5 V", "release_date": "2023-09-01", "variants": [
        {"ram": "8GB", "storage": "128GB", "chipset": "Snapdragon 8 Gen 2", "price": 84999},
    ]},
    {"brand": "Sony", "model_name": "Xperia 10 VI", "release_date": "2024-05-15", "variants": [
        {"ram": "6GB", "storage": "128GB", "chipset": "Snapdragon 6 Gen 1", "price": 34999},
    ]},

    # --- HONOR ---
    {"brand": "Honor", "model_name": "Honor Magic 6 Pro", "release_date": "2024-01-11", "variants": [
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 89999},
    ]},
    {"brand": "Honor", "model_name": "Honor Magic V3", "release_date": "2024-07-12", "variants": [
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8 Gen 3", "price": 149999},
    ]},
    {"brand": "Honor", "model_name": "Honor 200 Pro", "release_date": "2024-05-27", "variants": [
        {"ram": "12GB", "storage": "512GB", "chipset": "Snapdragon 8s Gen 3", "price": 57999},
    ]},
    {"brand": "Honor", "model_name": "Honor 200 5G", "release_date": "2024-05-27", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "Snapdragon 7 Gen 3", "price": 34999},
    ]},

    # --- INFINIX ---
    {"brand": "Infinix", "model_name": "Infinix GT 20 Pro", "release_date": "2024-05-21", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 8200 Ultimate", "price": 24999},
        {"ram": "12GB", "storage": "256GB", "chipset": "MediaTek Dimensity 8200 Ultimate", "price": 26999},
    ]},
    {"brand": "Infinix", "model_name": "Infinix Note 40 Pro+ 5G", "release_date": "2024-04-12", "variants": [
        {"ram": "12GB", "storage": "256GB", "chipset": "MediaTek Dimensity 7020", "price": 21999},
    ]},
    {"brand": "Infinix", "model_name": "Infinix Zero 30 5G", "release_date": "2023-09-01", "variants": [
        {"ram": "8GB", "storage": "256GB", "chipset": "MediaTek Dimensity 8020", "price": 23999},
    ]},
    {"brand": "Infinix", "model_name": "Infinix Smart 8 HD", "release_date": "2023-12-08", "variants": [
        {"ram": "3GB", "storage": "64GB", "chipset": "Unisoc T606", "price": 6299},
    ]}
]

def seed_famous_smartphones():
    db: Session = SessionLocal()
    try:
        print(f"[*] Starting ingestion of {len(SMARTPHONES_DATA)} famous smartphones into the database...")
        created_count = 0
        skipped_count = 0

        for item in SMARTPHONES_DATA:
            brand = DeduplicationService.normalize_brand(item["brand"])
            model_name = item["model_name"].strip()
            norm_key = DeduplicationService.generate_normalized_key(brand, model_name)

            existing, _ = DeduplicationService.find_existing_duplicate(db, brand, model_name)
            if existing:
                skipped_count += 1
                continue

            rel_date = None
            if item.get("release_date"):
                try:
                    rel_date = datetime.strptime(item["release_date"], "%Y-%m-%d").date()
                except Exception:
                    rel_date = date.today()

            product = Product(
                id=str(uuid.uuid4()),
                brand=brand,
                model_name=model_name,
                official_name=f"{brand} {model_name}",
                normalized_name=norm_key,
                release_date=rel_date,
                status="ACTIVE"
            )
            db.add(product)
            db.flush()

            for var in item.get("variants", []):
                variant = ProductVariant(
                    id=str(uuid.uuid4()),
                    product_id=product.id,
                    ram=var.get("ram"),
                    storage=var.get("storage"),
                    chipset=var.get("chipset"),
                    launch_price=Decimal(str(var.get("price"))) if var.get("price") else None,
                    currency="INR"
                )
                db.add(variant)

            created_count += 1

        db.commit()
        print(f"[+] Successfully seeded {created_count} smartphones into the database!")
        print(f"[-] Skipped {skipped_count} existing devices.")
    except Exception as e:
        db.rollback()
        print(f"[!] Error seeding smartphones: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_famous_smartphones()
