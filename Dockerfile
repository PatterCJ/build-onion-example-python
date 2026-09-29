# Assembled from what the hermetic build installed; nothing is fetched here.
FROM docker.io/library/python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
COPY dist/site /app
ENV PYTHONPATH=/app PYTHONDONTWRITEBYTECODE=1
ENTRYPOINT ["python", "-m", "pyonion.cli"]
