type ChatRequest = {
  messages: MessageData[];
  cpatcha: string | null;
};

type MessageData = {
  type: string;
  content: string;
  time: Number;
  sources: SourceSet;
  messageId: string;
  previousMessageId: string;
};

interface BaseMessage {
  sender: string;
  type: "start" | "end" | "error" | "stream";
}

interface StartMessage extends BaseMessage {
  messageId: string;
  previousMessageId: string;
  time: Number;
  type: "start";
}

interface EndMessage extends BaseMessage {
  messageId: string;
  previousMessageId: string;
  message: string;
  sources: SourceData[];
  type: "end";
}

interface ErrorMessage extends BaseMessage {
  message: string;
  type: "error";
}

interface StreamMessage extends BaseMessage {
  message: string;
  type: "stream";
}

type SourceSet = Record<string, SourceData>;

type SourceData = {
  chunk: number;
  date: string;
  link: string;
  name: string;
  page_number: number;
  type: string;
};

export {
  MessageData,
  SourceData,
  BaseMessage,
  StartMessage,
  EndMessage,
  ErrorMessage,
  StreamMessage,
  SourceSet,
  ChatRequest,
};
