# ---------- Base image ----------
FROM python:3.11-slim

# Avoid Python buffering logs
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# ---------- Workdir ----------
WORKDIR /app

# ---------- Install system deps (if needed) ----------
# If you don't need any system libs you can skip this,
# but it's nice to have gcc & lib openblas for some ML libs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# ---------- Install Python deps ----------
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn

# ---------- Copy project ----------
COPY . .

# Hugging Face will set $PORT; fallback to 7860 if not set
ENV PORT=7860

# ---------- Run app with gunicorn ----------
# Assumes create_app() is in app.py
# If your factory function/name is different, change "app:create_app()"
CMD bash -c "gunicorn -b 0.0.0.0:${PORT:-7860} 'app:create_app()'"
