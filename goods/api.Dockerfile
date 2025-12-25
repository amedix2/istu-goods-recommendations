FROM python:3.13-alpine

WORKDIR /src

COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

ENV PYTHONPATH=/src

RUN adduser -D appuser && chown -R appuser:appuser /src
USER appuser

COPY ./app ./app

CMD uv run granian \
    --interface asgi app.main:app \
    --host ${HOST:-0.0.0.0} \
    --port 8000 \
    --workers ${WORKERS:-4}