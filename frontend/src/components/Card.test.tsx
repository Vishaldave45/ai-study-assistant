import { describe, it, expect } from 'vitest';
import { render, screen } from '../test/test-utils';
import { Card } from './Card';

describe('Card Component', () => {
  it('renders children correctly inside the card container', () => {
    render(
      <Card>
        <h2>Card header</h2>
        <p>card content paragraph</p>
      </Card>
    );

    const heading = screen.getByRole('heading', { level: 2, name: /card header/i });
    const paragraph = screen.getByText(/card content paragraph/i);

    expect(heading).toBeInTheDocument();
    expect(paragraph).toBeInTheDocument();
  });
});

