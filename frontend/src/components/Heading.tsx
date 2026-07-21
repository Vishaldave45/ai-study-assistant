interface HeadingProps {
  title: string;
}

function Heading({ title }: HeadingProps) {
  return <h1>{title}</h1>;
}

export default Heading;