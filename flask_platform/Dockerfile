FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=7860

# Install system dependencies required by OpenMP and OpenCV/PIL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Set up non-root user (UID 1000) per Hugging Face Spaces security standard
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy dependency definition
COPY --chown=user:user requirements.txt .

# Install CPU PyTorch first to minimize build time and container size, then remaining dependencies
RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir --user -r requirements.txt

# Copy all application files, models, and assets
COPY --chown=user:user . .

# Expose default Hugging Face Spaces application port
EXPOSE 7860

# Launch production Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "--workers", "2", "--threads", "4", "--timeout", "120", "app:app"]
