#!/bin/sh
# Script to generate Python protobuf files

echo "Generating Python protobuf files..."

# Install grpcio-tools if not available
pip install --quiet grpcio-tools

# Generate protobuf files
python -m grpc_tools.protoc \
    -I../proto \
    --python_out=./proto \
    --grpc_python_out=./proto \
    ../proto/iot.proto

echo "✅ Protobuf files generated successfully!"
