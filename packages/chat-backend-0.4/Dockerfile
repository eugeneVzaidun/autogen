# Stage 1: Builder
FROM python:3.12.6-slim AS builder

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
# ENV POETRY_VERSION=1.4.2
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Set environment variables for Poetry
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry'

# Set work directory
WORKDIR /app

# Copy Poetry configuration files
COPY packages/chat-backend-0.4/pyproject.toml packages/chat-backend-0.4/poetry.lock* /app/
RUN ls -la
# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy application code
COPY packages/chat-backend-0.4/chat_backend_0.4/* /app/

# (Optional) Build the wheel
# RUN poetry build
# RUN pip install chat_backend-1.0.0-py3-none-any.whl


# Stage 2: Final Image
FROM python:3.12.6-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install runtime dependencies if any
# RUN apt-get update && apt-get install -y --no-install-recommends <runtime-packages> && \
#     rm -rf /var/lib/apt/lists/*

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code from builder
COPY --from=builder /app /app

# Create a non-root user
RUN addgroup --system appgroup && adduser --system appuser --ingroup appgroup

RUN chown -R appuser:appgroup /app

# Change to the non-root user
USER appuser

# Expose the port your application runs on
EXPOSE 80

# Define the command to run your application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
