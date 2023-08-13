import React, { useState } from "react";
import Message from "./message";
import { MessageApiResponse, MessageData, SourceSet } from "./types";

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
        />
        <button id="send-button" className={inFlight ? "disabled" : "enabled"}>
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

  const previousMessage = pastMessages.slice(-1);

  const messages = [
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
  fetch("/get_response", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(messages),
  })
    .then((response) => response.json())
    .then((data) =>
      receiveChatMessage(data, messages, setMessages, setInFlight)
    )
    .catch((error) => console.error("Error:", error));
  setText("");
}

function receiveChatMessage(
  data: MessageApiResponse,
  pastMessages: MessageData[],
  setMessages: React.Dispatch<React.SetStateAction<MessageData[]>>,
  setInFlight: React.Dispatch<React.SetStateAction<boolean>>
) {
  if (data.status != "SUCCESS") {
  }

  const uniqueSources: SourceSet = {};
  data.sources.forEach(
    (element) =>
      (uniqueSources[`${element.link}-page-${element.page_number.toString()}`] =
        element)
  );

  const messages = [
    ...pastMessages,
    {
      type: "ai",
      content: data.answer,
      time: Date.now(),
      sources: uniqueSources,
      messageId: data.messageId,
      previousMessageId: data.previousMessageId,
    },
  ];
  setMessages(messages);
  setInFlight(false);
}

export default Chat;
