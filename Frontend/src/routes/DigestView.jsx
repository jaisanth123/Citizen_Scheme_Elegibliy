import React from 'react';
import { useDigestController } from '../controllers/useDigestController';
import { FileText, Download, RotateCw, AlertCircle } from 'lucide-react';
import { apiClient } from '../api/apiClient';

export function DigestView() {
  const {
    digests,
    loading,
    generating,
    selectedTopic,
    setSelectedTopic,
    dateStr,
    setDateStr,
    activeDigest,
    setActiveDigest,
    error,
    generateNewDigest
  } = useDigestController();

  const topics = ['Technology', 'Health & Medicine', 'Science & Space', 'Social Media Hoaxes', 'Climate & Energy'];

  const handleExport = (digestId) => {
    window.open(apiClient.getDigestExportUrl(digestId), '_blank');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Title */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Daily Verified News Digest</h1>
        <p className="text-sm text-slate-600 mt-1">
          Compile verified claims and factual news into a daily intelligence briefing. Digests are saved directly to the database and exported via Model Context Protocol (MCP).
        </p>
      </div>

      {/* Generator Control Card */}
      <div className="bg-white border border-slate-200 rounded-sm p-5 mb-6 shadow-xs">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <label className="block text-2xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                Digest Topic:
              </label>
              <select
                value={selectedTopic}
                onChange={(e) => setSelectedTopic(e.target.value)}
                className="text-xs bg-white border border-slate-300 rounded-sm px-3 py-2 text-slate-800 focus:outline-hidden focus:border-slate-800"
              >
                {topics.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-2xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                Digest Date:
              </label>
              <input
                type="date"
                value={dateStr}
                onChange={(e) => setDateStr(e.target.value)}
                className="text-xs bg-white border border-slate-300 rounded-sm px-3 py-1.5 text-slate-800 focus:outline-hidden focus:border-slate-800"
              />
            </div>
          </div>

          <button
            onClick={generateNewDigest}
            disabled={generating}
            className={`flex items-center gap-2 px-5 py-2 text-xs font-bold uppercase tracking-wider text-white rounded-sm transition-all ${
              generating ? 'bg-slate-400 cursor-not-allowed' : 'bg-slate-900 hover:bg-slate-800 shadow-xs'
            }`}
          >
            {generating ? (
              <>
                <RotateCw className="w-4 h-4 animate-spin text-emerald-400" />
                <span>Compiling Digest...</span>
              </>
            ) : (
              <>
                <FileText className="w-4 h-4" />
                <span>Compile & Save via MCP</span>
              </>
            )}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-3 rounded-sm mb-6 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-700" />
          <span>{error}</span>
        </div>
      )}

      {/* Main Two-Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Digest Index Feed */}
        <div className="lg:col-span-4 space-y-3">
          <span className="text-2xs font-bold uppercase tracking-wider text-slate-500 block mb-1">
            Archived Daily Digests ({digests.length})
          </span>

          {loading && digests.length === 0 ? (
            <div className="bg-white border border-slate-200 p-6 text-center text-xs text-slate-500">
              Loading digests...
            </div>
          ) : digests.length === 0 ? (
            <div className="bg-white border border-slate-200 p-6 text-center text-xs text-slate-500">
              No digests compiled yet. Click 'Compile & Save via MCP' above.
            </div>
          ) : (
            digests.map((d) => {
              const isSelected = activeDigest?.id === d.id;
              return (
                <div
                  key={d.id}
                  onClick={() => setActiveDigest(d)}
                  className={`p-4 border rounded-sm cursor-pointer transition-all ${
                    isSelected
                      ? 'bg-slate-900 border-slate-900 text-white shadow-xs'
                      : 'bg-white border-slate-200 text-slate-800 hover:border-slate-400'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span
                      className={`text-2xs font-bold uppercase px-2 py-0.5 rounded ${
                        isSelected ? 'bg-slate-800 text-emerald-400' : 'bg-slate-100 text-slate-700'
                      }`}
                    >
                      {d.topic}
                    </span>
                    <span className={`text-2xs font-mono ${isSelected ? 'text-slate-400' : 'text-slate-500'}`}>
                      {d.date_str}
                    </span>
                  </div>
                  <h4 className="text-xs font-semibold leading-snug line-clamp-2">{d.title}</h4>
                  <div className="mt-2 text-2xs flex items-center justify-between">
                    <span className={isSelected ? 'text-slate-400' : 'text-slate-500'}>
                      {d.claim_count} verified items
                    </span>
                    <span className={`font-mono ${isSelected ? 'text-slate-400' : 'text-slate-400'}`}>
                      ID: {d.id}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Right Column: Markdown Document Viewer */}
        <div className="lg:col-span-8">
          {activeDigest ? (
            <div className="bg-white border border-slate-200 rounded-sm shadow-xs overflow-hidden">
              {/* Document Action Bar */}
              <div className="bg-slate-900 text-white px-5 py-3.5 flex items-center justify-between border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold">{activeDigest.title}</span>
                </div>
                <button
                  onClick={() => handleExport(activeDigest.id)}
                  className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-sm border border-slate-700 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Download .md (MCP)</span>
                </button>
              </div>

              {/* Raw Markdown / Rendered View */}
              <div className="p-6">
                <pre className="font-mono text-xs text-slate-800 bg-slate-50 p-4 rounded-sm border border-slate-200 whitespace-pre-wrap leading-relaxed overflow-x-auto">
                  {activeDigest.markdown_content}
                </pre>
              </div>
            </div>
          ) : (
            <div className="bg-white border border-slate-200 p-12 text-center text-xs text-slate-500">
              Select a digest from the left feed or generate a new one.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
