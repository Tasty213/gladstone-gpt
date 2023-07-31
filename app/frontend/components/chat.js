import React, { useState } from "react";
import Message from "./message";

function Chat() {
  const [text, setText] = useState("");
  const [pastMessages, setMessages] = useState([]);
  const [inFlight, setInFlight] = useState(false);

  return (
    <div id="chat-container">
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
        id="user-input"
        onSubmit={(e) =>
          sendChatMessage(e, text, pastMessages, setMessages, setInFlight)
        }
        autocomplete="off"
      >
        <input
          type="text"
          id="user-input-box"
          value={text}
          placeholder="Type your message here"
          onChange={(e) => setText(e.target.value)}
        />
        <button id="send-button" class={inFlight ? "disabled" : "enabled"}>
          Send
        </button>
      </form>
    </div>
  );
}

function sendChatMessage(event, text, pastMessages, setMessages, setInFlight) {
  event.preventDefault();

  setInFlight(true);
  var messages = [
    ...pastMessages,
    { type: "human", content: text, time: Date.now(), sources: [] },
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
}

function receiveChatMessage(data, pastMessages, setMessages, setInFlight) {
  if (data.status != "SUCCESS") {
  }

  let uniqueSources = {};
  data.sources.forEach(
    (element) =>
      (uniqueSources[`${element.link}-page-${element.page_number}`] = element)
  );

  var messages = [
    ...pastMessages,
    {
      type: "ai",
      content: data.answer,
      time: Date.now(),
      sources: uniqueSources,
    },
  ];
  setMessages(messages);
  setInFlight(false);
}

export default Chat;
