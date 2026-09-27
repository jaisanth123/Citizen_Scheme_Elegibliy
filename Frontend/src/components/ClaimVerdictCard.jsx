import React from 'react';
import { StatusBadge } from './StatusBadge';
import { ExternalLink, Download, CheckCircle, XCircle, ShieldAlert } from 'lucide-react';
import { apiClient } from '../api/apiClient';

export function ClaimVerdictCard({ claim }) {
  const confidencePercent = Math.round((claim.confidence || 0.5) * 100);

  let confidenceColor = 'bg-slate-600';
  if (confidencePercent >= 85) confidenceColor = 'bg-emerald-600';
  else if (confidencePercent >= 65) confidenceColor = 'bg-amber-600';
  else confidenceColor = 'bg-rose-600';

  const handleExport = () => {
    window.open(apiClient.getClaimExportUrl(claim.id), '_blank');
  };

  return (
    <article className="bg-white border border-slate-200 rounded-sm mb-6 shadow-xs overflow-hidden">
      {/* Top Banner */}
      <div className="bg-slate-900 text-white px-5 py-3.5 flex flex-wrap items-center justify-between gap-3 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <StatusBadge verdict={claim.verdict} size="lg" />
          <span className="text-xs text-slate-400 font-mono">ID: {claim.id}</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400 uppercase font-medium">Confidence:</span>
            <div className="w-24 bg-slate-800 h-2 rounded-sm overflow-hidden">
              <div className={`h-full ${confidenceColor}`} style={{ width: `${confidencePercent}%` }} />
            </div>
            <span className="text-xs font-mono font-bold text-white">{confidencePercent}%</span>
          </div>
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 rounded-sm border border-slate-700 transition-colors"
            title="Export as Markdown via MCP"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export MD</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="p-6">
        {/* Proposition Statement */}
        <div className="mb-5">
          <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Evaluated Proposition:</span>
          <h2 className="text-base font-semibold text-slate-900 bg-slate-50 p-3.5 rounded-sm border border-slate-200">
            "{claim.claim_text}"
          </h2>
        </div>

        {/* Executive Summary */}
        <div className="mb-6">
          <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-1">Reasoned Verdict Analysis:</span>
          <p className="text-sm text-slate-700 leading-relaxed bg-white border-l-4 border-slate-800 pl-4 py-1">
            {claim.summary}
          </p>
        </div>

        {/* Critic Review Note */}
        {claim.critic_notes && (
          <div className="mb-6 bg-slate-50 border border-slate-200 p-3 rounded-sm flex items-start gap-2.5 text-xs text-slate-700">
            <ShieldAlert className="w-4 h-4 text-slate-600 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-slate-900 block">Editorial Critic Audit:</span>
              <span>{claim.critic_notes}</span>
              {claim.reflection_rounds > 0 && (
                <span className="ml-1 text-slate-500 font-mono">({claim.reflection_rounds} reflection loops executed)</span>
              )}
            </div>
          </div>
        )}

        {/* Dual-Sided Evidence Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Supporting Evidence */}
          <div className="border border-slate-200 rounded-sm bg-slate-50 p-4">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-200">
              <CheckCircle className="w-4 h-4 text-emerald-700" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Supporting Evidence ({claim.supporting_evidence?.length || 0})
              </h4>
            </div>

            {claim.supporting_evidence && claim.supporting_evidence.length > 0 ? (
              <div className="space-y-3">
                {claim.supporting_evidence.map((item, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 p-3 rounded-sm text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-slate-900 truncate">{item.title}</span>
                      <span className="text-2xs font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded shrink-0">
                        {item.domain}
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs mb-2 line-clamp-3">{item.snippet}</p>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-2xs text-slate-700 hover:text-black font-semibold"
                    >
                      <span>View Source</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic p-2">No substantiated supporting evidence identified.</p>
            )}
          </div>

          {/* Contradicting Evidence */}
          <div className="border border-slate-200 rounded-sm bg-slate-50 p-4">
            <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-200">
              <XCircle className="w-4 h-4 text-rose-700" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-800">
                Contradicting Evidence ({claim.contradicting_evidence?.length || 0})
              </h4>
            </div>

            {claim.contradicting_evidence && claim.contradicting_evidence.length > 0 ? (
              <div className="space-y-3">
                {claim.contradicting_evidence.map((item, idx) => (
                  <div key={idx} className="bg-white border border-slate-200 p-3 rounded-sm text-xs">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-semibold text-slate-900 truncate">{item.title}</span>
                      <span className="text-2xs font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded shrink-0">
                        {item.domain}
                      </span>
                    </div>
                    <p className="text-slate-600 text-xs mb-2 line-clamp-3">{item.snippet}</p>
                    <a
                      href={item.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-2xs text-slate-700 hover:text-black font-semibold"
                    >
                      <span>View Source</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic p-2">No official counter-evidence or refutations found.</p>
            )}
          </div>
        </div>

        {/* Sources & Citations */}
        {claim.sources && claim.sources.length > 0 && (
          <div className="pt-3 border-t border-slate-200">
            <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-2">Authoritative Citations:</span>
            <div className="flex flex-wrap gap-2">
              {claim.sources.map((s, idx) => (
                <a
                  key={idx}
                  href={s.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-800 px-2.5 py-1 rounded-sm transition-colors"
                >
                  <span className="font-medium truncate max-w-xs">{s.title || s.domain}</span>
                  <span className="text-2xs font-mono text-slate-500">
                    ({Math.round((s.credibility_score || 0.8) * 100)}%)
                  </span>
                  <ExternalLink className="w-3 h-3 text-slate-400" />
                </a>
              ))}
            </div>
          </div>
        )}
      </div>
    </article>
  );
}
