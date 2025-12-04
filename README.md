# Feature 5 – Climate Impact & Anomaly Detector (Flask)

This is a standalone implementation of **Feature 5: Climate Impact & Anomaly Detector**
with a Flask UI and a small trainable anomaly model.

## What "training the model" means here

- `ClimateDataManager.generate_training_history()` produces multi-year synthetic daily climate data
  with features: `tavg`, `rain`, `spi`, `spei`.
- `ClimateAnomalyModel.train()` computes a mean/std vector and a Gaussian anomaly threshold.
- On app startup, we train the anomaly model once and then use it to score recent climate data.

In production you can replace this module with:
- Multimodal transformers over satellite + weather + soil + bulletins + user inputs.
- TFT / Informer models for temporal anomaly forecasting.
- Bayesian ensembles for uncertainty-aware thresholds.

## Running locally

```bash
cd feature5_climate_anomaly
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5005` in your browser.

## Integration notes

- Import `create_app` into your unified agro_features_suite backend or behind a FastAPI gateway.
- Replace `ClimateDataManager` stubs with real:
  - Open-Meteo weather, Sentinel-2/MODIS NDVI/EVI, Copernicus terrain.
  - NewsAPI free tier / FAO bulletins.
  - EuroCropsML crop patterns.
  - SPI / SPEI indices and extreme event datasets (NASA FIRMS, global flood archives).
- Replace `ClimateAnomalyModel` with your multimodal transformer + TFT/Informer architecture.
- Keep the UI and output schema; they are designed to be compatible with more advanced backends.
