import React, { useState } from "react";
import Message from "./message";
import {
  StartMessage,
  BaseMessage,
  MessageData,
  SourceSet,
  StreamMessage,
  EndMessage,
  ErrorMessage,
} from "./types";
import { Console } from "console";

type ChatProps = {
  userId: string;
};

function Chat({ userId }: ChatProps) {
  const [text, setText] = useState("");
  const [pastMessages, setMessages] = useState<MessageData[]>([]);
  const [inFlight, setInFlight] = useState(false);

  return (
    <div>
      <div id="chat-log">
        {pastMessages.map((message) => (
          <Message
            type={message.type}
            content={message.content}
            sources={message.sources}
          />
        ))}
      </div>
      <form
        className="user-input-form"
        onSubmit={(e) =>
          sendChatMessage(
            e,
            text,
            pastMessages,
            userId,
            setMessages,
            setInFlight,
            setText
          )
        }
        autoComplete="off"
      >
        <input
          type="text"
          className="user-input-box"
          value={text}
          placeholder="Type your message here"
          onChange={(e) => setText(e.target.value)}
          disabled={inFlight}
        />
        <button
          id="send-button"
          className={inFlight ? "disabled" : "enabled"}
          disabled={inFlight}
        >
          Send
        </button>
      </form>
    </div>
  );
}

function sendChatMessage(
  event: React.FormEvent<HTMLFormElement>,
  text: string,
  pastMessages: MessageData[],
  userId: string,
  setMessages: React.Dispatch<React.SetStateAction<MessageData[]>>,
  setInFlight: React.Dispatch<React.SetStateAction<boolean>>,
  setText: React.Dispatch<React.SetStateAction<string>>
) {
  event.preventDefault();

  setInFlight(true);
  setText("");

  const previousMessage = pastMessages.slice(-1);

  var messages = [
    ...pastMessages,
    {
      type: "human",
      content: text,
      time: Date.now(),
      sources: {},
      userId: userId,
      messageId: crypto.randomUUID().toString(),
      previousMessageId:
        previousMessage[0] === undefined
          ? "null"
          : previousMessage[0].messageId,
    },
  ];
  setMessages(messages);

  // Send the user message to the server

  const chatSocket = new WebSocket(`wss://${document.location.host}/chat`);
  chatSocket.onopen = (event) => {
    chatSocket.send(JSON.stringify(messages));
  };
  chatSocket.onmessage = (event) => {
    const message: BaseMessage = JSON.parse(event.data);
    switch (message.type) {
      case "start":
        messages = process_start_message(
          message as StartMessage,
          setMessages,
          messages
        );
        break;
      case "stream":
        process_stream_message(message as StreamMessage, setMessages, messages);
        break;
      case "end":
        process_end_message(message as EndMessage, setMessages, messages);
        break;
      case "error":
        process_error_message(message as ErrorMessage, setMessages, messages);
        break;
      default:
        console.log("default");
        break;
    }
  };
  chatSocket.onclose = (event) => {
    setInFlight(false);
  };
}

function process_start_message(
  message: StartMessage,
  setMessages: React.Dispatch<React.SetStateAction<MessageData[]>>,
  pastMessages: MessageData[]
) {
  const messages: MessageData[] = [
    ...pastMessages,
    {
      type: "ai",
      time: message.time,
      messageId: message.messageId,
      previousMessageId: message.previousMessageId,
      content: "",
      sources: {},
    },
  ];
  setMessages(messages);
  return messages;
}

function process_stream_message(
  message: StreamMessage,
  setMessages: React.Dispatch<React.SetStateAction<MessageData[]>>,
  pastMessages: MessageData[]
) {
  var messages: MessageData[] = [...pastMessages];
  messages[messages.length - 1].content =
    messages[messages.length - 1].content + message.message;
  setMessages(messages);
}

function process_end_message(
  message: EndMessage,
  setMessages: React.Dispatch<React.SetStateAction<MessageData[]>>,
  pastMessages: MessageData[]
) {
  var messages: MessageData[] = [...pastMessages];
  var final_message = messages[messages.length - 1];

  const uniqueSources: SourceSet = {};
  message.sources.forEach(
    (element) =>
      (uniqueSources[`${element.link}-page-${element.page_number.toString()}`] =
        element)
  );
  final_message.sources = uniqueSources;
  final_message.content = message.message;
  setMessages(messages);
}

function process_error_message(
  message: ErrorMessage,
  setMessages: React.Dispatch<React.SetStateAction<MessageData[]>>,
  pastMessages: MessageData[]
) {
  var messages: MessageData[] = [...pastMessages];
  var final_message = messages[messages.length - 1];
  final_message.content = message.message;
  setMessages(messages);
}

export default Chat;
