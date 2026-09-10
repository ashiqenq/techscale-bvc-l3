# TechScale: Multi-stage Docker build
# Stage 1 installs dependencies. Stage 2 is the lean runtime image.
# Only the installed packages and application code should reach the final image.


# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /build

# TODO: Copy the requirements file and install all dependencies.
# Install into an isolated location so they can be copied cleanly to the runtime stage.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# Stage 2: Runtime
# TODO: Start from a clean python:3.11-slim base.
# Copy only the installed packages from the builder stage — not the build tools or cache.
# Copy the application source, set the working directory, expose port 8000, and define the startup command.
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app ./app
ENV PYTHONPATH=/app/app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
