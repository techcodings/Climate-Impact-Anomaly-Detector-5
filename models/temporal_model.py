from typing import Dict, List
from datetime import datetime, timedelta
import math
from .data_loader import WeatherPoint

class ClimateTemporalModel:
    """Temporal forecasting stub for climate anomalies (TFT / Informer-ready)."""

    def __init__(self, config_cls):
        self.cfg = config_cls

    def forecast_anomalies(
        self,
        weather_series: List[WeatherPoint],
        climate_indices: Dict,
        scenario: str,
    ) -> Dict:
        if not weather_series:
            raise ValueError("Empty weather series")

        last_60 = weather_series[-60:]
        avg_temp = sum(p.tavg for p in last_60) / len(last_60)
        avg_rain = sum(p.rain for p in last_60) / len(last_60)

        scenario_temp_shift = {"baseline": 0.0, "hotter": 2.0, "drier": 1.0, "wetter": -0.5}.get(scenario, 0.0)
        scenario_rain_shift = {"baseline": 0.0, "hotter": -5.0, "drier": -10.0, "wetter": 15.0}.get(scenario, 0.0)

        forecast = []
        today = datetime.today()
        for i in range(self.cfg.DAYS_FORECAST):
            d = today + timedelta(days=i)
            season = math.sin(2 * math.pi * d.timetuple().tm_yday / 365.0)
            temp = avg_temp + scenario_temp_shift + 3 * season
            rain = max(0.0, avg_rain + scenario_rain_shift * (i / self.cfg.DAYS_FORECAST) + 5 * (1 - season))
            drought_prob = max(0.0, min(1.0, (30 - rain) / 50.0))
            flood_prob = max(0.0, min(1.0, (rain - 60) / 50.0))
            heatwave_prob = max(0.0, min(1.0, (temp - 32) / 10.0))
            forecast.append(
                {
                    "date": d.strftime("%Y-%m-%d"),
                    "temp": round(temp, 1),
                    "rain": round(rain, 1),
                    "drought_prob": round(drought_prob, 2),
                    "flood_prob": round(flood_prob, 2),
                    "heatwave_prob": round(heatwave_prob, 2),
                }
            )

        return {
            "forecast": forecast,
        }
