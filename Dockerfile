FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY rick_monitor.py .
COPY firebase_admin_setup.py .
COPY wagmi-crypto-calls-firebase-adminsdk-fbsvc-88527b62f1.json .

# Railway does not allow VOLUME, so we skip that
# If your app needs sessions, use a file-based fallback or /tmp

ENV SESSION=user_session2

# Expose health check port
EXPOSE 8080

# Run the application
CMD ["python", "rick_monitor.py"]
