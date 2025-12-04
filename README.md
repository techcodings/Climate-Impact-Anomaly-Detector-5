---
title: "Feature 5 – Climate Impact & Anomaly Detector"
emoji: 🌍
colorFrom: green
colorTo: yellow
sdk: docker
pinned: false
---

# 🌍 Feature 5 – Climate Impact & Anomaly Detector

This is a Flask-based demo app that simulates **climate impact and anomaly detection** for agricultural fields.

It uses synthetic climate & crop signals, temporal models, and rule-based / ML-like logic (see `models/`) to:
- Ingest region, crop and scenario
- Fuse synthetic climate features and impact models
- Detect anomalies & generate impact summaries
- Render visualizations (plots) into `static/generated/`
- Show results in a simple web UI

---

## 🔧 Tech Stack

- **Python 3.11**
- **Flask** for the web app
- **Matplotlib / NumPy / etc.** for visualization & synthetic data
- **Gunicorn** as the production WSGI server (for Hugging Face Spaces – Docker)

---

## 🗂 Project Structure

```text
.
├── app.py            # Flask entrypoint (exposes create_app())
├── requirements.txt  # Python dependencies
├── Dockerfile        # Hugging Face Space config (Docker)
├── models/           # Config, data loader, models, RL, image generator
├── static/
│   ├── css/style.css # Neon AgroVerse theme
│   ├── js/main.js    # Optional JS (if used)
│   └── generated/    # Generated PNGs for plots
├── templates/
│   ├── base.html
│   ├── index.html    # Inputs form
│   └── results.html  # Result dashboard
└── README.md
