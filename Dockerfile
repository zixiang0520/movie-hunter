FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt PySocks socksio

# Copy application
COPY backend/ ./backend/
COPY web/ ./web/
COPY config/ ./config/
COPY desktop.py .

# Expose port
EXPOSE 8765

# Run
CMD ["python", "backend/main.py"]
