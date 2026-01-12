FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PORT=8000 \
	WORKERS=4

COPY requirements.txt ./
RUN apt-get update \
	&& apt-get install -y --no-install-recommends curl ca-certificates \
	&& rm -rf /var/lib/apt/lists/* \
	&& pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY intelligence/ intelligence/
COPY recovery/ recovery/
COPY dashboard/ dashboard/

# Use an unprivileged user for runtime
RUN adduser --disabled-password --gecos "" appuser
USER appuser

EXPOSE 8000
ENTRYPOINT ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker -w ${WORKERS:-4} -b 0.0.0.0:${PORT:-8000} app.main:app"]
