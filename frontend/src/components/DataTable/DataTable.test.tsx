import { describe, it, expect } from 'vitest';

interface TestRecord {
  id: string;
  name: string;
  category: string;
}

const mockData: TestRecord[] = [
  { id: '1', name: 'Physics Notes.pdf', category: 'Physics' },
  { id: '2', name: 'Chemistry Summary.docx', category: 'Chemistry' },
];

describe('TanStack DataTable Data Transformation', () => {
  it('filters data by search query correctly', () => {
    const query = 'Physics';
    const filtered = mockData.filter((item) => item.name.includes(query));
    expect(filtered.length).toBe(1);
    expect(filtered[0].name).toBe('Physics Notes.pdf');
  });

  it('sorts records alphabetically', () => {
    const sorted = [...mockData].sort((a, b) => a.name.localeCompare(b.name));
    expect(sorted[0].name).toBe('Chemistry Summary.docx');
    expect(sorted[1].name).toBe('Physics Notes.pdf');
  });
});
