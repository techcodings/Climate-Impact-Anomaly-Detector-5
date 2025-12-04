from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict
import random
import pandas as pd

@dataclass
class WeatherPoint:
    date: datetime
    tavg: float
    rain: float
    wind: float

@dataclass
class NDVIPoint:
    date: datetime
    ndvi: float
    evi: float

class ClimateDataManager:
    """Synthetic data manager matching the climate feature's backend contracts.

    In production, replace stubs with:
    - Open-Meteo historical + forecast
    - Sentinel-2 / MODIS NDVI/EVI
    - Copernicus soil/terrain
    - NewsAPI / FAO climate bulletins
    - EuroCropsML historical crop patterns
    - SPI / SPEI indices
    - NASA FIRMS / global flood datasets
    """

    def __init__(self, config_cls):
        self.cfg = config_cls

    # -------- training history for anomaly model ----------
    def generate_training_history(self) -> pd.DataFrame:
        """Generate synthetic multi-year daily climate history for training."""
        today = datetime.today()
        start = today - timedelta(days=self.cfg.DAYS_HISTORY)
        rows = []
        for i in range(self.cfg.DAYS_HISTORY):
            d = start + timedelta(days=i)
            # Seasonal temperature pattern + noise
            temp = 20 + 10 * self._season_factor(d.timetuple().tm_yday) + random.gauss(0, 2)
            rain = max(0.0, random.gauss(3.0, 5.0))
            spi = random.gauss(0, 0.8)
            spei = spi + random.gauss(0, 0.3)
            rows.append(
                {
                    "date": d,
                    "tavg": temp,
                    "rain": rain,
                    "spi": spi,
                    "spei": spei,
                }
            )
        return pd.DataFrame(rows)

    def _season_factor(self, day_of_year: int) -> float:
        import math
        return math.sin(2 * math.pi * day_of_year / 365.0)

    # -------- main loaders ----------
    def load_weather_series(self, region: str) -> List[WeatherPoint]:
        today = datetime.today()
        start = today - timedelta(days=self.cfg.DAYS_HISTORY)
        series: List[WeatherPoint] = []
        for i in range(self.cfg.DAYS_HISTORY):
            d = start + timedelta(days=i)
            temp = 20 + 8 * self._season_factor(d.timetuple().tm_yday) + random.gauss(0, 1.5)
            rain = max(0.0, random.gauss(2.0, 4.0))
            wind = max(0.5, random.gauss(3.0, 1.0))
            series.append(WeatherPoint(date=d, tavg=temp, rain=rain, wind=wind))
        return series

    def load_ndvi_series(self, region: str) -> List[NDVIPoint]:
        today = datetime.today()
        start = today - timedelta(days=365)
        series: List[NDVIPoint] = []
        base = 0.5 + (hash(region) % 20) / 100.0
        for i in range(365):
            d = start + timedelta(days=i)
            season = self._season_factor(d.timetuple().tm_yday)
            ndvi = max(0.1, min(0.9, base + 0.3 * season + random.uniform(-0.05, 0.05)))
            evi = max(0.05, min(0.8, ndvi - 0.05 + random.uniform(-0.02, 0.02)))
            series.append(NDVIPoint(date=d, ndvi=ndvi, evi=evi))
        return series

    def load_soil_terrain(self, region: str) -> Dict:
        slope = round(1 + (hash(region + "slope") % 15), 1)
        aspect_deg = (hash(region + "aspect") % 360)
        elevation = 100 + (hash(region + "elev") % 500)
        erodibility_index = max(0.1, min(1.0, 0.2 + slope / 20.0))
        return {
            "slope_deg": slope,
            "aspect_deg": aspect_deg,
            "elevation_m": elevation,
            "erodibility_index": round(erodibility_index, 2),
        }

    def load_climate_indices(self, region: str) -> Dict:
        """Synthetic SPI/SPEI index time series."""
        today = datetime.today()
        start = today - timedelta(days=self.cfg.DAYS_HISTORY)
        spi_series = []
        spei_series = []
        for i in range(self.cfg.DAYS_HISTORY):
            d = start + timedelta(days=i)
            spi = random.gauss(0, 0.9)
            spei = spi + random.gauss(0, 0.3)
            spi_series.append({"date": d, "spi": spi})
            spei_series.append({"date": d, "spei": spei})
        return {"spi": spi_series, "spei": spei_series}

    def load_extreme_events(self, region: str) -> Dict:
        """Synthetic extreme events inspired by NASA FIRMS & flood datasets."""
        events = []
        today = datetime.today()
        for offset in [200, 120, 60, 20]:
            d = today - timedelta(days=offset)
            kind = random.choice(["fire", "flood", "heatwave", "storm"])
            severity = random.choice(["moderate", "severe", "extreme"])
            events.append(
                {
                    "date": d,
                    "type": kind,
                    "severity": severity,
                }
            )
        return {"events": events}

    def load_bulletins(self, region: str) -> Dict:
        """Sample NewsAPI/FAO-like bulletins."""
        today = datetime.today().strftime("%Y-%m-%d")
        return {
            "items": [
                {
                    "date": today,
                    "source": "FAO synthetic",
                    "title": "Regional drought watch bulletin",
                    "summary": "Below-normal rainfall observed in the last month; close monitoring recommended.",
                },
                {
                    "date": today,
                    "source": "NewsAPI synthetic",
                    "title": "Heatwave conditions reported in nearby districts",
                    "summary": "Daytime temperatures exceeded long-term averages by 4-5°C.",
                },
            ]
        }

    def load_crop_patterns(self, region: str) -> Dict:
        patterns = ["Cereal rotation", "Paddy-wheat rotation", "Oilseed dominated", "Mixed cropping"]
        return {
            "region": region,
            "dominant_pattern": patterns[hash(region) % len(patterns)],
            "historical_yield_sensitivity": {
                "drought": round(random.uniform(0.1, 0.4), 2),
                "flood": round(random.uniform(0.05, 0.3), 2),
                "heatwave": round(random.uniform(0.1, 0.35), 2),
            },
        }

    def load_metadata(self) -> Dict:
        return {
            "sources": [
                "Open-Meteo historical & forecast climate (synthetic stub)",
                "Sentinel-2 / MODIS NDVI/EVI (synthetic stub)",
                "Copernicus soil & terrain (offline stub)",
                "NewsAPI & FAO climate bulletins (synthetic summaries)",
                "EuroCropsML historical crop patterns (offline stub)",
                "SPI / SPEI indices (synthetic)",
                "NASA FIRMS & global flood archives (synthetic events)",
            ],
            "note": "Replace stubs with actual EO, climate, and news feeds in production.",
        }
