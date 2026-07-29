import { describe, it, expect } from 'vitest';
import { render, screen } from '../../../test/test-utils';
import { SummaryGenerator } from './SummaryGenerator';

describe('SummaryGenerator Component', () => {
  it('renders welcome message when no active workspace is selected', () => {
    render(<SummaryGenerator />);

    expect(
      screen.getByText(/please select a workspace to generate ai study summaries\./i)
    ).toBeInTheDocument();
  });
});
