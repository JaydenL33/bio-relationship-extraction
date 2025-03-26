# Use the NVIDIA PyTorch base image
FROM nvcr.io/nvidia/pytorch:25.02-py3 AS rag_base

# Set environment variables for Python and pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Builder stage to generate requirements.txt
FROM rag_base AS builder

# Install system dependencies required for Poetry installation
RUN apt-get update && apt-get install --no-install-recommends -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry to export dependencies
 RUN pip install "poetry==2.1.1"

# Set working directory and copy dependency files
WORKDIR /app
COPY app/pyproject.toml app/poetry.lock* ./
# Add Poetry to PATH

# Install Export Poetry Plugin
RUN poetry self add poetry-plugin-export

# Export dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt

# Development stage
FROM rag_base AS development

# Set environment variable for FastAPI
ENV FASTAPI_ENV=development

# Set working directory
WORKDIR /app

# Copy the generated requirements.txt from the builder stage
COPY --from=builder /app/requirements.txt .

# Install dependencies using pip
RUN pip install -r requirements.txt

# Copy application code
COPY ./app /app/app/

# Expose port and define the command to run the app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production stage
FROM rag_base AS production

# Set environment variable for FastAPI
ENV FASTAPI_ENV=production

# Set working directory
WORKDIR /app

# Copy the generated requirements.txt from the builder stage
COPY --from=builder /app/requirements.txt .

# Install dependencies using pip
RUN pip install -r requirements.txt

# Copy application code
COPY ./app /app/app/

# Install Gunicorn (assuming it’s not in pyproject.toml; adjust if it is)
RUN pip install gunicorn

# Expose port and define the command to run the app
EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"]