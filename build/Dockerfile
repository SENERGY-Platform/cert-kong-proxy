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
COPY --from=builder /app/cert_kong_proxy cert_kong_proxy
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/cert_kong_proxy

EXPOSE 5000

ARG ENV
ENV ENV={ENV}

CMD [ "python3", "-u", "-m", "flask", "run", "--host=0.0.0.0" ]

# Development image
FROM python:3.8 AS dev
WORKDIR /app
COPY --from=builder /app/version.txt .
COPY --from=builder /app/cert_kong_proxy cert_kong_proxy
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app/cert_kong_proxy

EXPOSE 5000

ARG ENV
ENV ENV={ENV}

CMD [ "python3", "-u", "-m", "flask", "run", "--host=0.0.0.0", "--debugger"]

# Test images
FROM python:3.8 AS test
WORKDIR /app
COPY --from=builder /app/version.txt .
COPY --from=builder /app/cert_kong_proxy ./cert_kong_proxy
COPY --from=builder /opt/venv /opt/venv

COPY tests ./tests

COPY build/run_tests.sh run_tests.sh

# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

RUN pip3 install coverage

EXPOSE 5000

ENV ENV=test

CMD [ "sh", "run_tests.sh" ]