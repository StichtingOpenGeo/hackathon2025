import type { ConnectRouter, HandlerContext } from "@connectrpc/connect";
import { TravelChatService } from "./gen/mainService_pb";
import { PingService } from "gen/pingService_pb";

export default (router: ConnectRouter) => {
  // registers connectrpc.eliza.v1.ElizaService
  router.service(TravelChatService, {
    // implements rpc Say
    async sendInput(req) {
      return {
        success: true,
      };
    },

    // Make a streaming call for getFeedback
    /* async getFeedback(req, context: HandlerContext) {
      setInterval(() => {
        
      }, 1000);
    }, */
  });

  router.service(PingService, {
    // implements rpc Say
    async serviceAvailable(req) {
      return {
        message: req.message,
      };
    },
  });
};
