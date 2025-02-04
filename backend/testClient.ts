import { createClient } from "@connectrpc/connect";
import { createConnectTransport } from "@connectrpc/connect-node";
import { TravelChatService } from "gen/mainService_pb";

const transport = createConnectTransport({
  baseUrl: "http://localhost:9990",
  httpVersion: "1.1",
});

async function main() {
  const client = createClient(TravelChatService, transport);
  const res = await client.sendInput({
    input: {
      case: "stringInput",
      value: { value: "Hello" },
    },
  });
  console.log(res);
}
void main();
