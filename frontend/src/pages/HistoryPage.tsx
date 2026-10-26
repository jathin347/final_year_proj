import React, { useState, useEffect } from 'react';
import { AnalysisHistorySummary } from '../types';
import { fetchHistory, deleteHistoryRecord } from '../api/client';
import { History, Trash2, ExternalLink, ChevronLeft, ChevronRight, RefreshCw, AlertCircle } from 'lucide-react';

interface Props {
  onSelectRecord: (id: string) => void;
}

export const HistoryPage: React.FC<Props> = ({ onSelectRecord }) => {
  const [items, setItems] = useState<AnalysisHistorySummary[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async (targetPage: number) => {
    setIsLoading(true);
    setError(null);
    try {
      const resp = await fetchHistory(targetPage, 10);
      setItems(resp.items);
      setPage(resp.page);
      setTotalPages(resp.pages);
      setTotalCount(resp.total);
    } catch (err: any) {
      setError(err.message || 'Failed to load verification history.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData(page);
  }, [page]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!window.confirm('Are you sure you want to delete this verification record?')) return;
    try {
      await deleteHistoryRecord(id);
      loadData(page);
    } catch (err: any) {
      alert(`Deletion failed: ${err.message}`);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center space-x-2.5">
            <History className="w-5 h-5 text-purple-400" />
            <h1 className="text-2xl font-extrabold text-white">Verification History</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Historical audit records stored in SQLite database. Total runs logged: {totalCount}
          </p>
        </div>
        <button
          onClick={() => loadData(page)}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition-colors"
          title="Refresh table"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
        </button>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-red-950/40 border border-red-900/60 text-red-300 text-xs flex items-center space-x-2 mb-6">
          <AlertCircle className="w-4 h-4 shrink-0 text-red-400" />
          <span>{error}</span>
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950 border-b border-slate-800 text-slate-400 font-mono">
              <tr>
                <th className="py-3.5 px-4 font-medium">Claim / Headline</th>
                <th className="py-3.5 px-4 font-medium">Domain</th>
                <th className="py-3.5 px-4 font-medium">Final Assessment</th>
                <th className="py-3.5 px-4 font-medium">Source Score</th>
                <th className="py-3.5 px-4 font-medium">Timestamp</th>
                <th className="py-3.5 px-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {isLoading ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500 font-mono">
                    Loading records from SQLite...
                  </td>
                </tr>
              ) : items.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-8 text-center text-slate-500">
                    No verification records found in the database. Run an analysis from the dashboard.
                  </td>
                </tr>
              ) : (
                items.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => onSelectRecord(item.id)}
                    className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                  >
                    <td className="py-3.5 px-4 font-medium text-white max-w-xs truncate">
                      {item.headline}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono">
                      {item.domain || 'N/A'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-950 border border-slate-800 text-slate-200">
                        {item.final_assessment}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono">
                      {item.source_credibility_score !== null && item.source_credibility_score !== undefined
                        ? `${item.source_credibility_score}/100`
                        : 'N/A'}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end space-x-2">
                        <button
                          onClick={() => onSelectRecord(item.id)}
                          className="p-1.5 rounded hover:bg-slate-800 text-blue-400 transition-colors"
                          title="View Verification Report"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={(e) => handleDelete(item.id, e)}
                          className="p-1.5 rounded hover:bg-red-950/60 text-slate-400 hover:text-red-400 transition-colors"
                          title="Delete Record"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400 font-mono">
          <span>
            Page {page} of {totalPages || 1}
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page <= 1}
              className="p-1.5 rounded border border-slate-800 hover:bg-slate-900 disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages}
              className="p-1.5 rounded border border-slate-800 hover:bg-slate-900 disabled:opacity-30 disabled:hover:bg-transparent"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
