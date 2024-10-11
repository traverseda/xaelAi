# Use the official Python image as base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy only the necessary files for Poetry first to utilize Docker cache
COPY pyproject.toml poetry.lock ./

# Install project dependencies (without virtualenv creation)
RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application code
COPY ./xaelai/ .

# Expose the port the application runs on (optional, if applicable)
# EXPOSE 8000

# Set the entrypoint or command for the container
CMD streamlit run app.py
