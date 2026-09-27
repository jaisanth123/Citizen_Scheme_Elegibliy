import React from 'react';
import { useArchiveController } from '../controllers/useArchiveController';
import { StatusBadge } from '../components/StatusBadge';
import { Search, Download, Database, ShieldCheck } from 'lucide-react';
import { apiClient } from '../api/apiClient';

export function ArchiveView() {
  const {
    claims,
    sources,
    loading,
    searchQuery,
    setSearchQuery,
    selectedVerdict,
    setSelectedVerdict,
    activeTab,
    setActiveTab
  } = useArchiveController();

  const verdictOptions = ['All', 'True', 'False', 'Misleading', 'Unverifiable'];

  const handleExport = (claimId) => {
    window.open(apiClient.getClaimExportUrl(claimId), '_blank');
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Knowledge Base & Intelligence Archive</h1>
        <p className="text-sm text-slate-600 mt-1">
          Explore previously verified claims stored in the database and audit the accredited sources in the RAG knowledge registry.
        </p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-slate-200 mb-6 space-x-4">
        <button
          onClick={() => setActiveTab('claims')}
          className={`pb-3 text-sm font-bold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'claims'
              ? 'border-slate-900 text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Database className="w-4 h-4" />
          <span>Previously Checked Claims ({claims.length})</span>
        </button>

        <button
          onClick={() => setActiveTab('sources')}
          className={`pb-3 text-sm font-bold flex items-center gap-2 border-b-2 transition-colors ${
            activeTab === 'sources'
              ? 'border-slate-900 text-slate-900'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <ShieldCheck className="w-4 h-4" />
          <span>Trusted Sources & Bias Registry ({sources.length})</span>
        </button>
      </div>

      {activeTab === 'claims' ? (
        <div>
          {/* Filter Bar */}
          <div className="bg-white border border-slate-200 rounded-sm p-4 mb-6 shadow-xs flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2 flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-400" />
              <input
                type="text"
                placeholder="Search claims by keyword..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full text-xs p-2 border border-slate-300 rounded-sm focus:outline-hidden focus:border-slate-800"
              />
            </div>

            <div className="flex items-center gap-2">
              <span className="text-2xs font-bold uppercase tracking-wider text-slate-500">Verdict:</span>
              <div className="flex space-x-1">
                {verdictOptions.map((opt) => (
                  <button
                    key={opt}
                    onClick={() => setSelectedVerdict(opt)}
                    className={`text-xs px-2.5 py-1 rounded-sm border transition-colors ${
                      selectedVerdict === opt
                        ? 'bg-slate-900 text-white border-slate-900 font-semibold'
                        : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    {opt}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Claims List Table */}
          {loading ? (
            <div className="bg-white border border-slate-200 p-8 text-center text-xs text-slate-500">
              Loading claims from MCP database...
            </div>
          ) : claims.length === 0 ? (
            <div className="bg-white border border-slate-200 p-8 text-center text-xs text-slate-500">
              No matching claims found.
            </div>
          ) : (
            <div className="bg-white border border-slate-200 rounded-sm shadow-xs overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs text-slate-700">
                  <thead className="bg-slate-900 text-white uppercase text-2xs tracking-wider">
                    <tr>
                      <th className="px-4 py-3">Verdict</th>
                      <th className="px-4 py-3">Claim Statement</th>
                      <th className="px-4 py-3">Category</th>
                      <th className="px-4 py-3">Confidence</th>
                      <th className="px-4 py-3">Sources</th>
                      <th className="px-4 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {claims.map((c) => (
                      <tr key={c.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-4 py-3 whitespace-nowrap">
                          <StatusBadge verdict={c.verdict} size="sm" />
                        </td>
                        <td className="px-4 py-3 max-w-md">
                          <p className="font-semibold text-slate-900 line-clamp-2">{c.claim_text}</p>
                          <p className="text-2xs text-slate-500 mt-0.5 line-clamp-1">{c.summary}</p>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap">
                          <span className="text-2xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded font-medium">
                            {c.category || 'General'}
                          </span>
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap font-mono font-bold">
                          {Math.round(c.confidence * 100)}%
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-slate-500">
                          {c.sources?.length || 0} citations
                        </td>
                        <td className="px-4 py-3 whitespace-nowrap text-right">
                          <button
                            onClick={() => handleExport(c.id)}
                            className="inline-flex items-center gap-1 text-2xs bg-slate-100 hover:bg-slate-200 text-slate-800 px-2.5 py-1 rounded-sm border border-slate-300 transition-colors"
                            title="Download Markdown report via MCP"
                          >
                            <Download className="w-3 h-3" />
                            <span>Export MD</span>
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Trusted Sources Directory */
        <div className="bg-white border border-slate-200 rounded-sm shadow-xs overflow-hidden">
          <div className="p-4 bg-slate-50 border-b border-slate-200">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Verified Information Outlets & Media Reliability Index
            </h3>
            <p className="text-2xs text-slate-500 mt-0.5">
              The Evidence Retriever assigns credibility multipliers to evidence matching these domains and audits for media bias.
            </p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-700">
              <thead className="bg-slate-900 text-white uppercase text-2xs tracking-wider">
                <tr>
                  <th className="px-4 py-3">Source Name</th>
                  <th className="px-4 py-3">Domain</th>
                  <th className="px-4 py-3">Credibility Score</th>
                  <th className="px-4 py-3">Bias Rating</th>
                  <th className="px-4 py-3">Category</th>
                  <th className="px-4 py-3">Editorial Notes</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {sources.map((s, idx) => (
                  <tr key={idx} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-semibold text-slate-900">{s.name}</td>
                    <td className="px-4 py-3 font-mono text-slate-600">{s.domain}</td>
                    <td className="px-4 py-3 whitespace-nowrap font-mono font-bold text-emerald-700">
                      {Math.round(s.credibility_score * 100)}%
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-2xs bg-slate-100 text-slate-800 px-2 py-0.5 rounded font-mono">
                        {s.bias_rating}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-slate-600">{s.category}</td>
                    <td className="px-4 py-3 text-slate-500 text-2xs max-w-xs">{s.notes}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
