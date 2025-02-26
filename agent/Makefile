.PHONY: protoc mqtt-server ws-server
protoc:
	uv run python -m grpc_tools.protoc -I./proto --python_out=./proto --pyi_out=./proto proto/*.proto

mqtt-server:
	docker run -p 1883:1883 -p 8083:8083 -p 8084:8084 -p 8883:8883 -p 18083:18083 emqx/emqx:latest

ws-server:
	uv run python -m ws_server
