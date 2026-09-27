import React from 'react';
import { useFactCheckController, SAMPLE_QUERIES } from '../controllers/useFactCheckController';
import { PipelineVisualizer } from '../components/PipelineVisualizer';
import { ClaimVerdictCard } from '../components/ClaimVerdictCard';
import { Search, RotateCw, AlertTriangle, Trash2 } from 'lucide-react';

export function FactCheckView() {
  const {
    inputText,
    setInputText,
    isAnalyzing,
    activeStep,
    reflectionRound,
    logs,
    result,
    error,
    maxReflections,
    setMaxReflections,
    handleSelectSample,
    runAnalysis,
    clearResults
  } = useFactCheckController();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Editorial Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">Multi-Agent Fact Verification Desk</h1>
        <p className="text-sm text-slate-600 mt-1">
          Paste any statement, forwarded WhatsApp message, or news excerpt. The LangGraph agent splits claims, searches Tavily & RAG archives, weighs dual-sided evidence, and undergoes editorial critic reflection.
        </p>
      </div>

      {/* Input Form Card */}
      <div className="bg-white border border-slate-200 rounded-sm p-6 mb-6 shadow-xs">
        <div className="mb-4">
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
            Input Text / Forwarded Message / Claim
          </label>
          <textarea
            rows={4}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="e.g. Is it true that drinking hot water cures viral infections? Or paste forwarded text..."
            className="w-full text-sm p-3.5 border border-slate-300 rounded-sm focus:outline-hidden focus:border-slate-800 text-slate-900 bg-white placeholder:text-slate-400"
          />
        </div>

        {/* Quick Presets */}
        <div className="mb-5">
          <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-2">
            Sample Verification Presets:
          </span>
          <div className="flex flex-wrap gap-2">
            {SAMPLE_QUERIES.map((sq, idx) => (
              <button
                key={idx}
                onClick={() => handleSelectSample(sq.query)}
                className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-800 px-3 py-1.5 rounded-sm border border-slate-200 transition-colors text-left"
              >
                {sq.title}
              </button>
            ))}
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-slate-100">
          <div className="flex items-center gap-3">
            <label className="text-xs font-medium text-slate-600">Critic Reflection Depth:</label>
            <select
              value={maxReflections}
              onChange={(e) => setMaxReflections(Number(e.target.value))}
              className="text-xs bg-white border border-slate-300 rounded-sm px-2.5 py-1 text-slate-800 focus:outline-hidden focus:border-slate-800"
            >
              <option value={1}>1 Reflection Round</option>
              <option value={2}>2 Reflection Rounds (Standard)</option>
              <option value={3}>3 Reflection Rounds (Deep Audit)</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            {(result || logs.length > 0) && (
              <button
                onClick={clearResults}
                className="flex items-center gap-1.5 px-3 py-2 text-xs text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-sm border border-slate-300 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                <span>Clear</span>
              </button>
            )}

            <button
              onClick={runAnalysis}
              disabled={!inputText.trim() || isAnalyzing}
              className={`flex items-center gap-2 px-5 py-2 text-xs font-bold uppercase tracking-wider text-white rounded-sm transition-all ${
                !inputText.trim() || isAnalyzing
                  ? 'bg-slate-400 cursor-not-allowed'
                  : 'bg-slate-900 hover:bg-slate-800 shadow-xs'
              }`}
            >
              {isAnalyzing ? (
                <>
                  <RotateCw className="w-4 h-4 animate-spin text-emerald-400" />
                  <span>Verifying Evidence...</span>
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  <span>Execute Verification</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="bg-rose-50 border border-rose-200 text-rose-800 p-4 rounded-sm mb-6 flex items-start gap-3 text-xs">
          <AlertTriangle className="w-4 h-4 text-rose-700 shrink-0 mt-0.5" />
          <div>
            <span className="font-bold block">Verification Error:</span>
            <span>{error}</span>
          </div>
        </div>
      )}

      {/* LangGraph Pipeline Status */}
      {(isAnalyzing || logs.length > 0) && (
        <PipelineVisualizer
          activeStep={activeStep}
          reflectionRound={reflectionRound}
          logs={logs}
        />
      )}

      {/* Results Section */}
      {result && result.results && (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-800">
              Verified Proposition Analysis ({result.results.length})
            </h2>
            <span className="text-xs text-slate-500 font-mono">
              Completed at {new Date(result.timestamp).toLocaleTimeString()}
            </span>
          </div>

          {result.results.map((claim) => (
            <ClaimVerdictCard key={claim.id} claim={claim} />
          ))}
        </div>
      )}
    </div>
  );
}
