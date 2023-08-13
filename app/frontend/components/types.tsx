type MessageData = {
  type: string;
  content: string;
  time: Number;
  sources: SourceSet;
  messageId: string;
  previousMessageId: string;
};

type MessageApiResponse = {
  answer: string;
  messageId: string;
  previousMessageId: string;
  sources: SourceData[];
  status: string;
};

type SourceSet = Record<string, SourceData>;

type SourceData = {
  chunk: number;
  date: string;
  link: string;
  name: string;
  page_number: number;
  type: string;
};

export { MessageData, SourceData, MessageApiResponse, SourceSet };
