import type { ConnectRouter, HandlerContext } from "@connectrpc/connect";
import { TravelChatService } from "./gen/mainService_pb";
import { PingService } from "gen/pingService_pb";

export default (router: ConnectRouter) => {
  // registers connectrpc.eliza.v1.ElizaService
  router.service(TravelChatService, {
    // implements rpc Say
    async sendInput(req) {
      console.log(req);
      return {
        success: true,
      };
    },

    // Make a streaming call for getFeedback
    /* async getFeedback(call) {
      setInterval(() => {
        call.write({ message: "hello" });
      }, 1000);
    }, */
  });

  router.service(PingService, {
    // implements rpc Say
    async serviceAvailable(req) {
      console.log(req);
      return {
        message: req.message,
      };
    },
  });
};
