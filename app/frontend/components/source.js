function Source({ name, link, page }) {
  if (page) {
    name = `${name} - page ${page}`;
  }

  return (
    <div className="source">
      <a href={link}>{name}</a>
    </div>
  );
}

export default Source;
