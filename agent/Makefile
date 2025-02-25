.PHONY: protoc
protoc:
	uv run python -m grpc_tools.protoc -I./proto --python_out=./proto --pyi_out=./proto proto/*.proto

mqtt-server:
	docker run -it -p 1883:1883 eclipse-mosquitto:latest mosquitto -c /mosquitto-no-auth.conf
