import Source from "./source";

function Message({ type, content, sources }) {
  return (
    <div className={`message ${type}`}>
      <p>{content}</p>
      <ul className="sources">
        {Object.entries(sources).map((source) => (
          <li>
            <Source
              name={source[1].name}
              link={source[1].link}
              page={source[1].page}
            />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Message;
