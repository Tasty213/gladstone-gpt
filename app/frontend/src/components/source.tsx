type SourceProps = {
  name: string;
  link: string;
  page: string;
  key: string;
};

function Source({ name, link, page, key }: SourceProps) {
  name = page != "0" ? `${name} - page ${page}` : name;

  return (
    <li className="source" key={name}>
      <a href={link}>{name}</a>
    </li>
  );
}

export default Source;
