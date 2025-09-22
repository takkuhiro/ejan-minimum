FROM python:3.12-slim AS base

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy and install dependencies
COPY pyproject.toml .
RUN uv pip compile pyproject.toml > requirements.txt
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Cloud Run sets PORT environment variable
ENV PORT 8000
EXPOSE $PORT

# Use PORT environment variable for Cloud Run compatibility
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
