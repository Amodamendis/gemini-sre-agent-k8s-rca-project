FROM python:3.11-slim
WORKDIR /app
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ /app/src/
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
CMD ["python", "src/main.py"]