.PHONY: protoc
protoc:
	uv run python -m grpc_tools.protoc -I./proto --python_out=./proto --pyi_out=./proto proto/*.proto
