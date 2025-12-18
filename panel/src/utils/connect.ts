import { io } from "socket.io-client";
import { serverURL } from "./config";
import PubSub from "pubsub-js";
import { pubMsg } from "./general";

// Build connection.
// Notion: the "transports" option is used to prevent "Access-Control-Allow-Origin" error.
export const socket = io(serverURL, {
  transports: ['websocket', 'polling', 'flashsocket']
});

socket.io.on("error", (error) => {
  pubMsg("连接失败", "建立与服务端的连接失败", "error", 3);
});

socket.on("alert-message", (args) => {
  args.title = args.title || "Server Message";
  args.type = args.type || "info";
  args.dur = args.dur || 3;
  pubMsg(args.title, args.str, args.type, args.dur);
});

socket.on("confirm-connect", (arg) => {
  console.log(socket.id);
});
