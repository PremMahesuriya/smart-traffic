FROM python:3.10-slim

# Install compilation tools and basic system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code files
COPY . .

# Run the unified orchestrator script pointing to the local mock video
CMD ["python", "main.py", "--video", "datasets/day.mp4"]
