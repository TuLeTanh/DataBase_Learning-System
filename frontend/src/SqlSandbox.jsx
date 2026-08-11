import React, { useState } from 'react';

const API_BASE_URL = "http://127.0.0.1:8000";

export default function SqlSandbox({ activeSessionId, t }) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRun = async () => {
    if (!query.trim()) return;
    setIsLoading(true);
    setError(null);
    setResults(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/sandbox/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          session_id: activeSessionId,
          query: query
        })
      });

      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Error executing query");
      } else {
        setResults(data.result);
      }
    } catch (e) {
      setError("Network error or server down.");
    } finally {
      setIsLoading(false);
    }
  };

  const renderTable = () => {
    if (!results) return null;
    
    // If it's a dict like {"rows_affected": X}
    if (!Array.isArray(results) && results.rows_affected !== undefined) {
      return (
        <div className="text-emerald-400 font-medium">
          Success! Rows affected: {results.rows_affected}
        </div>
      );
    }

    if (!Array.isArray(results)) {
      return <div className="text-white/60">Unknown result format.</div>;
    }

    if (results.length === 0) {
      return <div className="text-white/60">0 rows returned.</div>;
    }

    const headers = Object.keys(results[0]);

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-white/80">
          <thead className="text-xs text-white/50 uppercase bg-white/5">
            <tr>
              {headers.map(h => (
                <th key={h} className="px-4 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {results.map((row, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                {headers.map(h => (
                  <td key={h} className="px-4 py-3 whitespace-nowrap">
                    {row[h] === null ? <span className="text-white/30">NULL</span> : String(row[h])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-full bg-[#0B101E]/50 p-6">
      <h2 className="text-xl font-bold text-white mb-2">SQL Sandbox</h2>
      <p className="text-white/50 text-sm mb-4">
        Practice your SQL here. Each chat session has its own isolated SQLite database.
        Use CREATE, INSERT, SELECT, UPDATE, DELETE to explore.
      </p>

      <div className="flex-1 flex flex-col gap-4">
        {/* Editor Area */}
        <div className="relative flex flex-col flex-shrink-0 bg-[#0B101E] border border-white/10 rounded-xl overflow-hidden focus-within:border-accent-500/50 transition-colors">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="SELECT * FROM sqlite_master;"
            className="w-full h-40 bg-transparent text-white p-4 font-mono text-sm resize-none focus:outline-none"
            spellCheck="false"
          />
          <div className="bg-white/5 p-2 flex justify-end border-t border-white/10">
            <button
              onClick={handleRun}
              disabled={isLoading || !activeSessionId}
              className="px-4 py-1.5 bg-accent-600 hover:bg-accent-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg transition-colors focus-ring"
            >
              {isLoading ? "Running..." : "Run (F5)"}
            </button>
          </div>
        </div>

        {/* Results Area */}
        <div className="flex-1 bg-[#0B101E] border border-white/10 rounded-xl p-4 overflow-y-auto flex flex-col">
          <h3 className="text-xs font-semibold text-white/50 uppercase tracking-wider mb-3 shrink-0">Output</h3>
          {error && (
            <div className="text-red-400 bg-red-500/10 border border-red-500/20 p-3 rounded-lg font-mono text-sm whitespace-pre-wrap">
              {error}
            </div>
          )}
          {!error && !results && !isLoading && (
            <div className="text-white/30 text-sm italic m-auto">
              Results will appear here...
            </div>
          )}
          {!error && isLoading && (
            <div className="text-white/30 text-sm italic m-auto animate-pulse">
              Executing query...
            </div>
          )}
          {!error && !isLoading && renderTable()}
        </div>
      </div>
    </div>
  );
}
