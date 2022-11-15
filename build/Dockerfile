# Build image
FROM python:3.8 AS builder

WORKDIR /app

COPY . .

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install -r requirements.txt
RUN git log -1 --oneline > version.txt

# Production image
FROM python:3.8 AS prod
WORKDIR /app
COPY --from=builder /app/version.txt .
COPY --from=builder /app/server server
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
EXPOSE 5000

CMD [ "gunicorn", "--bind", "0.0.0.0:5000", "--chdir=server", "main:app"]

# Development image -> set debug levels
FROM prod AS dev
ARG ENV
ENV DEBUG=1
ENV FLASK_DEBUG=1

# Test images
FROM python:3.8 AS test
WORKDIR /app
COPY --from=builder /app/version.txt .
COPY --from=builder /app/server ./server
COPY --from=builder /opt/venv /opt/venv

COPY tests ./tests

COPY build/run_tests.sh run_tests.sh

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install coverage

EXPOSE 5000

ENV ENV=test

CMD [ "sh", "run_tests.sh" ]