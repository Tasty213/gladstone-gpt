import Source from "./source";
import { SourceSet } from "./types";

type MessageProps = {
  type: string;
  content: string;
  sources: SourceSet;
};

function Message({ type, content, sources }: MessageProps) {
  return (
    <div className={`message ${type}`}>
      <p>{content}</p>
      <ul className="sources">
        {Object.entries(sources).map((source) => (
          <Source
            name={source[1].name}
            link={source[1].link}
            page={source[1].page_number.toString()}
          />
        ))}
      </ul>
    </div>
  );
}

export default Message;
