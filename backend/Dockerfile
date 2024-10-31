# Use the official Python image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only the poetry files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

# Copy the application code
COPY app ./app

# Expose the port that the app runs on
EXPOSE 8000

# Set the entrypoint command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]