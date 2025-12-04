import os
from typing import List, Dict
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .data_loader import WeatherPoint

class ClimateImageGenerator:
    """Generates SPI/SPEI & anomaly visualization panels."""

    def __init__(self, config_cls):
        self.cfg = config_cls

    def generate_visualization(
        self,
        weather_series: List[WeatherPoint],
        climate_indices: Dict,
        temporal_out: Dict,
        anomaly_scores: List[Dict],
        anomaly_flags: Dict,
        impact_out: Dict,
        output_path: str,
    ):
        last_weather = weather_series[-120:]
        dates = [p.date for p in last_weather]
        temps = [p.tavg for p in last_weather]
        rain = [p.rain for p in last_weather]

        spi_series = climate_indices["spi"][-120:]
        spei_series = climate_indices["spei"][-120:]
        spi_dates = [x["date"] for x in spi_series]
        spi_vals = [x["spi"] for x in spi_series]
        spei_vals = [x["spei"] for x in spei_series]

        forecast = temporal_out.get("forecast", [])[:60]
        f_dates = [f["date"] for f in forecast]
        d_probs = [f["drought_prob"] for f in forecast]
        f_probs = [f["flood_prob"] for f in forecast]
        h_probs = [f["heatwave_prob"] for f in forecast]

        fig, axes = plt.subplots(2, 2, figsize=(11, 6))
        ax1, ax2, ax3, ax4 = axes.ravel()

        ax1.plot(dates, temps, label="Tavg (°C)")
        ax1.set_ylabel("Temp (°C)")
        ax1_twin = ax1.twinx()
        ax1_twin.bar(dates, rain, alpha=0.3)
        ax1_twin.set_ylabel("Rain (mm)")
        ax1.set_title("Recent Weather History")
        ax1.grid(True, alpha=0.3)

        ax2.plot(spi_dates, spi_vals, label="SPI")
        ax2.plot(spi_dates, spei_vals, linestyle="--", label="SPEI")
        ax2.axhline(-1.0, linestyle=":", linewidth=1)
        ax2.axhline(1.0, linestyle=":", linewidth=1)
        ax2.set_title("SPI / SPEI Trend (last 120 days)")
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.plot(f_dates, d_probs, label="Drought")
        ax3.plot(f_dates, f_probs, label="Flood")
        ax3.plot(f_dates, h_probs, label="Heatwave")
        ax3.set_title("Forecast Anomaly Probabilities (next 60 days)")
        ax3.set_ylabel("Probability")
        ax3.set_ylim(0, 1)
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis="x", rotation=45)

        ax4.axis("off")
        lines = [
            f"Drought anomaly: {anomaly_flags.get('drought_anomaly', False)}",
            f"Flood anomaly: {anomaly_flags.get('flood_anomaly', False)}",
            f"Heatwave anomaly: {anomaly_flags.get('heatwave_anomaly', False)}",
            "",
            f"Overall climate risk: {impact_out.get('overall_risk', 0.0):.2f} ({impact_out.get('risk_level', '')})",
            f"Expected yield impact: {impact_out.get('expected_yield_impact', 0.0):.2f} (fractional)",
            "",
            "Top alerts:",
        ]
        for al in impact_out.get("alerts", [])[:4]:
            lines.append(f"- {al}")
        ax4.text(0.02, 0.98, "\n".join(lines), va="top", ha="left")

        plt.tight_layout()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        fig.savefig(output_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
