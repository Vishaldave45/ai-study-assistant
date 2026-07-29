import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/test-utils';
import { Heading } from './Heading';

describe('Heading Component', () => {
  it('renders title text in an h1 heading element', () => {
    render(<Heading title="Study Dashboard" />);
    const heading = screen.getByRole('heading', { level: 1, name: /study dashboard/i });
    expect(heading).toBeInTheDocument();
  });
});
