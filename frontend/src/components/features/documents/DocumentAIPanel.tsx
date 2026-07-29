import React, { useState } from 'react';
import { Image, Table, Calculator, Sparkles, Zap } from 'lucide-react';

export interface DiagramItem {
  id: string;
  title: string;
  description: string;
  mermaidCode?: string;
  concepts: string[];
}

export interface TableItem {
  id: string;
  contentMarkdown: string;
}

export interface EquationItem {
  id: string;
  latex: string;
  explanation?: string;
}

export interface DocumentAIPanelProps {
  pageNumber: number;
  diagrams?: DiagramItem[];
  tables?: TableItem[];
  equations?: EquationItem[];
  onActionTrigger?: (actionType: string, payload: any) => void;
}

export const DocumentAIPanel: React.FC<DocumentAIPanelProps> = ({
  pageNumber,
  diagrams = [],
  tables = [],
  equations = [],
  onActionTrigger,
}) => {
  const [activeTab, setActiveTab] = useState<'diagrams' | 'tables' | 'equations'>('diagrams');

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 shadow-xl text-slate-100 font-sans">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-indigo-400" />
          <h3 className="text-lg font-semibold text-white">
            AI Document Intelligence — Page {pageNumber}
          </h3>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-indigo-500/20 text-indigo-300 font-medium">
          Multimodal Mode
        </span>
      </div>

      {/* Tabs Bar */}
      <div className="flex gap-2 mb-5 border-b border-slate-800 pb-2">
        <button
          onClick={() => setActiveTab('diagrams')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'diagrams'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Image className="w-4 h-4" />
          Diagrams ({diagrams.length})
        </button>

        <button
          onClick={() => setActiveTab('tables')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'tables'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Table className="w-4 h-4" />
          Tables ({tables.length})
        </button>

        <button
          onClick={() => setActiveTab('equations')}
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
            activeTab === 'equations'
              ? 'bg-indigo-600 text-white shadow-md'
              : 'bg-slate-800/60 text-slate-400 hover:text-slate-200'
          }`}
        >
          <Calculator className="w-4 h-4" />
          Equations ({equations.length})
        </button>
      </div>

      {/* Tab Contents */}
      <div className="space-y-4 min-h-[160px]">
        {/* Diagrams Tab */}
        {activeTab === 'diagrams' && (
          <div>
            {diagrams.length === 0 ? (
              <p className="text-slate-500 text-xs italic py-4">No visual diagrams detected on Page {pageNumber}.</p>
            ) : (
              diagrams.map((diag) => (
                <div key={diag.id} className="bg-slate-950/70 border border-slate-800/80 rounded-lg p-4 mb-3">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-bold text-indigo-300">{diag.title}</h4>
                    <button
                      onClick={() => onActionTrigger?.('generate_quiz', diag)}
                      className="flex items-center gap-1 text-[11px] bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 px-2.5 py-1 rounded transition-colors"
                    >
                      <Zap className="w-3 h-3" /> Quiz from Diagram
                    </button>
                  </div>
                  <p className="text-xs text-slate-400 mb-3">{diag.description}</p>

                  {diag.mermaidCode && (
                    <div className="bg-slate-900 border border-slate-800 rounded p-3 text-[11px] font-mono text-emerald-400 overflow-x-auto">
                      <pre>{diag.mermaidCode}</pre>
                    </div>
                  )}

                  {diag.concepts.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {diag.concepts.map((concept, idx) => (
                        <span key={idx} className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded">
                          {concept}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        )}

        {/* Tables Tab */}
        {activeTab === 'tables' && (
          <div>
            {tables.length === 0 ? (
              <p className="text-slate-500 text-xs italic py-4">No data tables detected on Page {pageNumber}.</p>
            ) : (
              tables.map((tbl) => (
                <div key={tbl.id} className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 mb-3 overflow-x-auto">
                  <pre className="text-xs text-slate-200 font-mono whitespace-pre-wrap">{tbl.contentMarkdown}</pre>
                </div>
              ))
            )}
          </div>
        )}

        {/* Equations Tab */}
        {activeTab === 'equations' && (
          <div>
            {equations.length === 0 ? (
              <p className="text-slate-500 text-xs italic py-4">No math equations detected on Page {pageNumber}.</p>
            ) : (
              equations.map((eq) => (
                <div key={eq.id} className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 mb-3">
                  <div className="text-sm font-mono text-amber-300 bg-slate-900 px-3 py-2 rounded mb-2">
                    $$ {eq.latex} $$
                  </div>
                  {eq.explanation && <p className="text-xs text-slate-400 italic">{eq.explanation}</p>}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};
