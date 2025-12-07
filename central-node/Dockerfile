# Base image
FROM python:3.11-slim as builder

WORKDIR /app

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install dependencies
COPY central-node/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy proto definition and generate Python files
COPY proto/iot.proto /tmp/iot.proto
RUN mkdir -p proto && \
    python -m grpc_tools.protoc \
    -I/tmp \
    --python_out=./proto \
    --pyi_out=./proto \
    --grpc_python_out=./proto \
    /tmp/iot.proto && \
    sed -i 's/^import iot_pb2/from . import iot_pb2/' proto/iot_pb2_grpc.py && \
    echo "from .iot_pb2 import SensorData, ServerResponse" > proto/__init__.py && \
    echo "from .iot_pb2_grpc import DataTransferServicer, add_DataTransferServicer_to_server" >> proto/__init__.py && \
    echo "__all__ = ['SensorData', 'ServerResponse', 'DataTransferServicer', 'add_DataTransferServicer_to_server']" >> proto/__init__.py

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/proto /app/proto

# Set environment to use venv
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy application code (excluding proto which is already copied)
COPY --chown=appuser:appuser central-node/database ./database
COPY --chown=appuser:appuser central-node/utils ./utils
COPY --chown=appuser:appuser central-node/server.py .

# Switch to non-root user
USER appuser

EXPOSE 50051

CMD ["python", "server.py"]
