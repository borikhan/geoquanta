FROM python:3.14-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app ./app
USER 65532:65532
EXPOSE 8080
CMD ["sh","-c","uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
