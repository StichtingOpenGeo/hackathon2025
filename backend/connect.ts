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

    async *getFeedback() {
      console.log("Feedback requested");
      yield {
        feedback: {
          case: "SentenceFeedback",
          value: {
            message: `Begin je reis te voet vanaf je startlocatie. Je loopt ongeveer 10 minuten tot je aankomt op Rotterdam Centraal, het eerste station op je reis. Vanaf hier stap je in op de Intercity Direct (ICD) richting Amersfoort Schothorst. De trein vertrekt vanaf spoor 12 om 12:46, wat iets later is dan gepland. Deze treinreis duurt ongeveer 31 minuten.

Zodra je om 13:18 aankomt op Amsterdam Zuid, vervolg je je reis te voet richting het metrostation binnen hetzelfde stationscomplex, een wandeling van een paar minuten. Hier neem je metrolijn 52 richting Noord. De metro vertrekt om 13:25 vanaf Amsterdam Zuid en de rit duurt ongeveer 8 minuten.

Je stapt uit bij de halte Rokin om 13:33. Het laatste deel van je reis leg je te voet af. Dit is een wandeling van ongeveer 14 minuten naar jouw eindbestemming.

Tijdens je reis is het belangrijk om goed te letten op borden en vertrektijden, vooral gezien er enkele vertragingen optreden. Veel reisplezier!`,
          },
        },
      };
    },
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
