FROM python:3.10-slim as base
RUN mkdir /opt/project
WORKDIR /opt/project
COPY app/ app/
COPY pyproject.toml poetry.lock .

FROM base as uvicorn
RUN pip install -U wheel poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main,uvicorn
CMD ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "--port", "80", "--log-level", "error", "app.main:app"]

FROM base as gunicorn
RUN pip install -U wheel poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main,gunicorn
CMD ["poetry", "run", "gunicorn", "--preload", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80", "--timeout", "0", "app.main:app"]
