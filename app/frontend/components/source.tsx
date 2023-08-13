type SourceProps = {
  name: string;
  link: string;
  page: string;
};

function Source({ name, link, page }: SourceProps) {
  name = page ? `${name} - page ${page}` : name;

  return (
    <li className="source" key={name}>
      <a href={link}>{name}</a>
    </li>
  );
}

export default Source;
