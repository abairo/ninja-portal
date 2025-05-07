FROM python:3.13.3-alpine

ARG INSTALL_DEV_DEPS=False

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false
WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN if [ "$INSTALL_DEV_DEPS" = "True" ]; then \
        poetry install --no-root; \
    else \
        poetry install --no-root --only main; \
    fi

COPY . .

EXPOSE 8000

CMD ["gunicorn", "api_gateway.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--workers", "4"]
