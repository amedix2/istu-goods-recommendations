FROM python:3.13-alpine

WORKDIR /src

COPY requirements/prod.txt .
COPY requirements/test.txt .
RUN pip install --no-cache-dir -r test.txt

ENV PYTHONPATH=/src

COPY ./app ./app
COPY ./tests ./tests

CMD ["pytest", "/src/tests/", "-v"]