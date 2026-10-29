from pathlib import Path

APP_NAME = "Мир одежды и аксессуаров"

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "mir_odezhdy",
    "user": "postgres",
    "password": "123",  
}

DISCOUNT_PERCENT = 25
LOW_STOCK_LIMIT = 3

BASE_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = BASE_DIR / "resources"
IMAGES_DIR = RESOURCES_DIR / "images"
LOGO_PATH = RESOURCES_DIR / "logo.png"
ICON_PATH = RESOURCES_DIR / "icon.ico"
PLACEHOLDER_PATH = RESOURCES_DIR / "picture.png"