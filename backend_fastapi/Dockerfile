# Use a lean official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables for best practices in containers
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_EXTRA_INDEX_URL=https://pypi.org/simple

# Install uv, a fast Python package installer
# We use pip to bootstrap uv itself.
RUN pip install uv

# Set the working directory in the container
WORKDIR /app

# Copy the project files into the container
# This includes pyproject.toml and the app directory
COPY . .

# Install dependencies using uv.
# --system installs them into the global site-packages.
# The '.' tells uv to install the project defined in the current directory.
RUN uv pip install --system .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# This uses the 'start_prod' script defined in pyproject.toml for production.
CMD ["prod"] 