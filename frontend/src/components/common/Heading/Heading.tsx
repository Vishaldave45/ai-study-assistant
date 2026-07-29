import { memo } from 'react';

interface HeadingProps {
  title: string;
}

export const Heading = memo(function Heading({ title }: HeadingProps) {
  return <h1>{title}</h1>;
});

export default Heading;