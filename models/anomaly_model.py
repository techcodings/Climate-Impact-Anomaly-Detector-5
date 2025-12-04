from typing import Dict, List, Tuple
import pandas as pd
import numpy as np
from .data_loader import WeatherPoint

class ClimateAnomalyModel:
    """Simple anomaly detector with a training routine.

    This acts as a placeholder for:
    - Multimodal transformer (satellite + weather + soil + news + user)
    - TFT / Informer anomaly prediction
    - Bayesian ensembles for uncertainty
    """

    def __init__(self, config_cls):
        self.cfg = config_cls
        self.mean_vec = None
        self.std_vec = None
        self.threshold = None

    def train(self, history_df: pd.DataFrame):
        """Train a very simple Gaussian anomaly model on synthetic history.

        Features: tavg, rain, spi, spei
        """
        feats = history_df[["tavg", "rain", "spi", "spei"]].values
        self.mean_vec = feats.mean(axis=0)
        self.std_vec = feats.std(axis=0) + 1e-6
        z_scores = np.abs((feats - self.mean_vec) / self.std_vec)
        baseline = np.mean(z_scores)
        self.threshold = baseline + 2.0  # simple cutoff

    def _ensure_trained(self):
        if self.mean_vec is None or self.std_vec is None or self.threshold is None:
            raise RuntimeError("Anomaly model not trained. Call train() first.")

    def score_series(
        self,
        weather_series: List[WeatherPoint],
        climate_indices: Dict,
        extreme_events: Dict,
        user_event: str,
    ) -> Tuple[List[Dict], Dict]:
        self._ensure_trained()

        spi_map = {item["date"].date(): item["spi"] for item in climate_indices["spi"]}
        spei_map = {item["date"].date(): item["spei"] for item in climate_indices["spei"]}

        scores: List[Dict] = []
        flags = {
            "drought_anomaly": False,
            "flood_anomaly": False,
            "heatwave_anomaly": False,
            "user_flagged_event": bool(user_event.strip()),
        }

        for p in weather_series[-90:]:
            spi = spi_map.get(p.date.date(), 0.0)
            spei = spei_map.get(p.date.date(), 0.0)
            vec = np.array([p.tavg, p.rain, spi, spei])
            z = np.abs((vec - self.mean_vec) / self.std_vec)
            score = float(z.mean())
            label = "normal"
            if score > self.threshold:
                # classify type from simple rules
                if spi < -1.0 or spei < -1.0:
                    label = "drought"
                    flags["drought_anomaly"] = True
                elif p.rain > 60:
                    label = "flood"
                    flags["flood_anomaly"] = True
                elif p.tavg > 35:
                    label = "heatwave"
                    flags["heatwave_anomaly"] = True
                else:
                    label = "generic"
            scores.append(
                {
                    "date": p.date.strftime("%Y-%m-%d"),
                    "tavg": round(p.tavg, 1),
                    "rain": round(p.rain, 1),
                    "spi": round(spi, 2),
                    "spei": round(spei, 2),
                    "score": round(score, 3),
                    "label": label,
                }
            )

        # incorporate extreme events
        for ev in extreme_events.get("events", []):
            kind = ev["type"]
            if kind == "fire":
                flags["heatwave_anomaly"] = True
            elif kind == "flood":
                flags["flood_anomaly"] = True
            elif kind == "heatwave":
                flags["heatwave_anomaly"] = True

        return scores, flags
