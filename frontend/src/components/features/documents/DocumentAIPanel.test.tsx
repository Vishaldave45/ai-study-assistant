import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { DocumentAIPanel } from './DocumentAIPanel';

describe('DocumentAIPanel Component', () => {
  const sampleDiagrams = [
    {
      id: 'diag-1',
      title: 'OSI Model Architecture',
      description: '7-layer protocol stack diagram.',
      mermaidCode: 'graph TD\n App --> Pres',
      concepts: ['Application', 'Presentation'],
    },
  ];

  const sampleTables = [
    {
      id: 'table-1',
      contentMarkdown: '| Layer | Protocol |\n| --- | --- |\n| TCP | Transport |',
    },
  ];

  const sampleEquations = [
    {
      id: 'eq-1',
      latex: 'E = mc^2',
      explanation: 'Mass energy equivalence.',
    },
  ];

  it('renders multimodal tabs and page title correctly', () => {
    render(
      <DocumentAIPanel
        pageNumber={5}
        diagrams={sampleDiagrams}
        tables={sampleTables}
        equations={sampleEquations}
      />
    );

    expect(screen.getByText('AI Document Intelligence — Page 5')).toBeInTheDocument();
    expect(screen.getByText('Diagrams (1)')).toBeInTheDocument();
    expect(screen.getByText('Tables (1)')).toBeInTheDocument();
    expect(screen.getByText('Equations (1)')).toBeInTheDocument();
  });

  it('displays diagram details and triggers action callback', () => {
    const handleAction = vi.fn();
    render(
      <DocumentAIPanel
        pageNumber={5}
        diagrams={sampleDiagrams}
        onActionTrigger={handleAction}
      />
    );

    expect(screen.getByText('OSI Model Architecture')).toBeInTheDocument();
    expect(screen.getByText('7-layer protocol stack diagram.')).toBeInTheDocument();

    const quizBtn = screen.getByText('Quiz from Diagram');
    fireEvent.click(quizBtn);

    expect(handleAction).toHaveBeenCalledWith('generate_quiz', sampleDiagrams[0]);
  });

  it('switches tabs to show table content', () => {
    render(
      <DocumentAIPanel
        pageNumber={5}
        diagrams={sampleDiagrams}
        tables={sampleTables}
      />
    );

    const tableTabBtn = screen.getByText('Tables (1)');
    fireEvent.click(tableTabBtn);

    expect(screen.getByText(/\| TCP \| Transport \|/)).toBeInTheDocument();
  });
});
