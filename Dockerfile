FROM python:3.12-slim

RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY src ./src

RUN pip install --no-cache-dir uv && \
    uv sync --frozen --no-dev

RUN chown -R appuser:appuser /app

USER appuser

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "events_aggregator.main:app", "--host", "0.0.0.0", "--port", "8000"]