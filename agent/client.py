import grpc
import mainService_pb2
import mainService_pb2_grpc
import userInput_pb2

def run():
    # Connect to the gRPC server
    channel = grpc.insecure_channel("localhost:50051")
    stub = mainService_pb2_grpc.TravelChatServiceStub(channel)

    while True:
        user_input = input("You: ")
        if user_input.lower() in {"exit", "quit"}:
            break

        # Create request object
        request = userInput_pb2.UserInput(stringInput=userInput_pb2.StringInput(value=user_input))

        # Call the gRPC method
        response = stub.sendInput(request)

        print(f"Assistant: {response}")

if __name__ == "__main__":
    run()
