FROM python:3.8 AS builder

WORKDIR /app

COPY . .
RUN pip3 install -r requirements.txt
RUN git log -1 --oneline > version.txt

FROM python:3.8
WORKDIR /app
COPY --from=builder /app/version.txt .
COPY --from=builder /app/app.py .

WORKDIR /app

EXPOSE 5000

ENTRYPOINT ["python3", "-u", "-m" , "flask", "run", "--host=0.0.0.0"]