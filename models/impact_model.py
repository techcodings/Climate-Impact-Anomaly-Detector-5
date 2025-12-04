from typing import Dict

class ImpactAssessor:
    """Maps detected anomalies to crop impact and risk scores."""

    def __init__(self, config_cls):
        self.cfg = config_cls

    def assess_impact(
        self,
        crop: str,
        anomaly_flags: Dict,
        climate_indices: Dict,
        extreme_events: Dict,
        crop_patterns: Dict,
    ) -> Dict:
        sens = crop_patterns.get("historical_yield_sensitivity", {})
        drought_sens = sens.get("drought", 0.2)
        flood_sens = sens.get("flood", 0.15)
        heatwave_sens = sens.get("heatwave", 0.2)

        drought_risk = drought_sens if anomaly_flags.get("drought_anomaly") else drought_sens * 0.4
        flood_risk = flood_sens if anomaly_flags.get("flood_anomaly") else flood_sens * 0.3
        heatwave_risk = heatwave_sens if anomaly_flags.get("heatwave_anomaly") else heatwave_sens * 0.4

        overall_risk = 1.0 - (1 - drought_risk) * (1 - flood_risk) * (1 - heatwave_risk)
        overall_risk = round(overall_risk, 2)

        expected_yield_impact = -round(overall_risk * 0.3, 2)

        alerts = []
        if anomaly_flags.get("drought_anomaly"):
            alerts.append("Drought-like anomaly detected in recent climate signals.")
        if anomaly_flags.get("flood_anomaly"):
            alerts.append("Flood-related conditions detected.")
        if anomaly_flags.get("heatwave_anomaly"):
            alerts.append("Heatwave-like conditions detected.")
        if anomaly_flags.get("user_flagged_event"):
            alerts.append("User reported a local extreme event. Prioritize ground-truth verification.")

        if overall_risk < 0.2:
            risk_level = "Low"
        elif overall_risk < 0.45:
            risk_level = "Moderate"
        else:
            risk_level = "High"

        return {
            "drought_risk": round(drought_risk, 2),
            "flood_risk": round(flood_risk, 2),
            "heatwave_risk": round(heatwave_risk, 2),
            "overall_risk": overall_risk,
            "risk_level": risk_level,
            "expected_yield_impact": expected_yield_impact,
            "alerts": alerts,
        }
