import os
import uuid
from datetime import datetime
from flask import Flask, render_template, request, flash
from models.config import Config
from models.data_loader import ClimateDataManager
from models.temporal_model import ClimateTemporalModel
from models.anomaly_model import ClimateAnomalyModel
from models.impact_model import ImpactAssessor
from models.rl_strategy import StrategyRLSimulator
from models.image_generator import ClimateImageGenerator

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")
    app.config["GENERATED_FOLDER"] = os.path.join("static", "generated")
    os.makedirs(app.config["GENERATED_FOLDER"], exist_ok=True)

    data_manager = ClimateDataManager(Config)
    temporal_model = ClimateTemporalModel(Config)
    anomaly_model = ClimateAnomalyModel(Config)
    impact_assessor = ImpactAssessor(Config)
    rl_simulator = StrategyRLSimulator(Config)
    image_generator = ClimateImageGenerator(Config)

    # Train the anomaly model once at startup on synthetic history
    historical_df = data_manager.generate_training_history()
    anomaly_model.train(historical_df)

    @app.route("/", methods=["GET", "POST"])
    def index():
        if request.method == "POST":
            try:
                region = request.form.get("region") or "Region-001"
                crop = request.form.get("crop") or "Maize"
                user_event = request.form.get("user_event") or ""
                scenario = request.form.get("scenario") or "baseline"

                weather_series = data_manager.load_weather_series(region=region)
                ndvi_series = data_manager.load_ndvi_series(region=region)
                soil_terrain = data_manager.load_soil_terrain(region=region)
                climate_indices = data_manager.load_climate_indices(region=region)
                extreme_events = data_manager.load_extreme_events(region=region)
                bulletins = data_manager.load_bulletins(region=region)
                crop_patterns = data_manager.load_crop_patterns(region=region)
                commons_data = data_manager.load_metadata()

                temporal_out = temporal_model.forecast_anomalies(
                    weather_series=weather_series,
                    climate_indices=climate_indices,
                    scenario=scenario,
                )

                anomaly_scores, anomaly_flags = anomaly_model.score_series(
                    weather_series=weather_series,
                    climate_indices=climate_indices,
                    extreme_events=extreme_events,
                    user_event=user_event,
                )

                impact_out = impact_assessor.assess_impact(
                    crop=crop,
                    anomaly_flags=anomaly_flags,
                    climate_indices=climate_indices,
                    extreme_events=extreme_events,
                    crop_patterns=crop_patterns,
                )

                rl_out = rl_simulator.simulate_strategies(
                    anomaly_flags=anomaly_flags,
                    impact_out=impact_out,
                )

                img_filename = f"climate_anomaly_{uuid.uuid4().hex}.png"
                img_path = os.path.join(app.config["GENERATED_FOLDER"], img_filename)
                rel_img_path = os.path.join("generated", img_filename)

                image_generator.generate_visualization(
                    weather_series=weather_series,
                    climate_indices=climate_indices,
                    temporal_out=temporal_out,
                    anomaly_scores=anomaly_scores,
                    anomaly_flags=anomaly_flags,
                    impact_out=impact_out,
                    output_path=img_path,
                )

                metrics = {
                    "drought_risk": impact_out.get("drought_risk", 0.0),
                    "flood_risk": impact_out.get("flood_risk", 0.0),
                    "heatwave_risk": impact_out.get("heatwave_risk", 0.0),
                    "overall_climate_risk": impact_out.get("overall_risk", 0.0),
                    "expected_yield_impact": impact_out.get("expected_yield_impact", 0.0),
                }

                return render_template(
                    "results.html",
                    region=region,
                    crop=crop,
                    scenario=scenario,
                    user_event=user_event,
                    metrics=metrics,
                    temporal_out=temporal_out,
                    anomaly_scores=anomaly_scores,
                    anomaly_flags=anomaly_flags,
                    impact_out=impact_out,
                    rl_out=rl_out,
                    image_path=rel_img_path,
                    bulletins=bulletins,
                    commons_data=commons_data,
                )
            except Exception as e:
                flash(f"Climate anomaly analysis failed: {e}", "danger")  # noqa: E501

        regions = ["Region-001", "Region-002", "Highland-Belt", "River-Valley"]
        crops = ["Maize", "Wheat", "Rice", "Soybean", "Cotton"]
        scenarios = [
            ("baseline", "Baseline"),
            ("hotter", "Warmer than normal"),
            ("drier", "Drier than normal"),
            ("wetter", "Wetter than normal"),
        ]
        return render_template(
            "index.html",
            regions=regions,
            crops=crops,
            scenarios=scenarios,
        )

    @app.route("/api/health")
    def health():
        return {"status": "ok", "feature": "climate_impact_anomaly_detector"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5005)), debug=True)
