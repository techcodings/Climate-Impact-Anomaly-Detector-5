import os

class Config:
    DEVICE = "cpu"

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    CACHE_DIR = os.path.join(BASE_DIR, "cache")

    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

    DAYS_HISTORY = 365 * 3
    DAYS_FORECAST = 60
    IMG_WIDTH = 1100
    IMG_HEIGHT = 650
