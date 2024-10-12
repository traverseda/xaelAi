# Use the official Python image as base
FROM python:3.11-slim

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only the necessary files for Poetry first to utilize Docker cache
COPY pyproject.toml poetry.lock ./

# Install project dependencies (without virtualenv creation)
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Install watchdog for auto-reloading
RUN pip install watchdog

# Copy the rest of the application code
COPY ./xaelai/ /app/xaelai

# Set the working directory inside the container
WORKDIR /app

# Set the PYTHONPATH environment variable
ENV PYTHONPATH=/app
CMD watchmedo auto-restart --directory=/app --pattern=*.py --recursive -- streamlit run xaelai/app.py

