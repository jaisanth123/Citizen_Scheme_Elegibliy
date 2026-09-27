import React from 'react';
import { useEvalController } from '../controllers/useEvalController';
import { StatusBadge } from '../components/StatusBadge';
import { CheckCircle2, XCircle, Play, RotateCw } from 'lucide-react';

export function EvaluationView() {
  const { testCases, report, isRunning, runBenchmark } = useEvalController();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900">Benchmark & Accuracy Evaluation</h1>
          <p className="text-sm text-slate-600 mt-1">
            Test the LangGraph pipeline and Critic reflection loop against a standardized ground-truth dataset of labeled factual claims, viral hoaxes, and unverified rumors.
          </p>
        </div>

        <button
          onClick={runBenchmark}
          disabled={isRunning}
          className={`flex items-center gap-2 px-5 py-2.5 text-xs font-bold uppercase tracking-wider text-white rounded-sm transition-all ${
            isRunning ? 'bg-slate-400 cursor-not-allowed' : 'bg-slate-900 hover:bg-slate-800 shadow-xs'
          }`}
        >
          {isRunning ? (
            <>
              <RotateCw className="w-4 h-4 animate-spin text-emerald-400" />
              <span>Running Benchmark...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 text-emerald-400" />
              <span>Execute Accuracy Test</span>
            </>
          )}
        </button>
      </div>

      {/* Metrics Scorecard */}
      {report && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-slate-900 text-white p-5 rounded-sm border border-slate-800 shadow-xs">
            <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Overall Benchmark Accuracy
            </span>
            <div className="text-3xl font-extrabold text-emerald-400 font-mono">
              {report.accuracy_percentage}%
            </div>
            <p className="text-2xs text-slate-400 mt-1">
              {report.correct_count} of {report.total_claims} claims correctly determined
            </p>
          </div>

          <div className="bg-slate-900 text-white p-5 rounded-sm border border-slate-800 shadow-xs">
            <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              "Unverifiable" Guardrail Rate
            </span>
            <div className="text-3xl font-extrabold text-white font-mono">
              {report.unverifiable_guardrail_rate}%
            </div>
            <p className="text-2xs text-slate-400 mt-1">
              Strict adherence to avoidance of speculation
            </p>
          </div>

          <div className="bg-slate-900 text-white p-5 rounded-sm border border-slate-800 shadow-xs">
            <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Test Run ID
            </span>
            <div className="text-sm font-bold text-slate-200 font-mono mt-2 truncate">
              {report.run_id}
            </div>
            <p className="text-2xs text-slate-400 mt-2 font-mono">
              {new Date(report.timestamp).toLocaleTimeString()}
            </p>
          </div>

          <div className="bg-slate-900 text-white p-5 rounded-sm border border-slate-800 shadow-xs">
            <span className="text-2xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
              Domain Categories Tested
            </span>
            <div className="text-sm font-semibold text-slate-300 mt-1 space-y-0.5">
              {Object.entries(report.per_category_accuracy || {}).map(([cat, score]) => (
                <div key={cat} className="flex justify-between text-2xs">
                  <span>{cat}:</span>
                  <span className="font-mono font-bold text-emerald-400">{score}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Dataset / Results Table */}
      <div className="bg-white border border-slate-200 rounded-sm shadow-xs overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-700">
            {report ? 'Evaluation Benchmark Run Results' : `Standard Evaluation Dataset (${testCases.length} Cases)`}
          </h3>
          <span className="text-2xs text-slate-500">
            {report ? 'Tested with dual-sided Evidence Retriever & Critic Reflection' : 'Pre-labeled ground truth claims'}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-700">
            <thead className="bg-slate-900 text-white uppercase text-2xs tracking-wider">
              <tr>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Claim Assertion</th>
                <th className="px-4 py-3">Ground Truth</th>
                {report && <th className="px-4 py-3">Predicted</th>}
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Rationale & Difficulty</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {report ? (
                report.results.map((res) => (
                  <tr key={res.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap">
                      {res.is_correct ? (
                        <span className="inline-flex items-center gap-1 text-2xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          <span>PASSED</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-2xs font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded">
                          <XCircle className="w-3.5 h-3.5" />
                          <span>FAILED</span>
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 max-w-sm font-medium text-slate-900">{res.claim}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge verdict={res.ground_truth} size="sm" />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge verdict={res.predicted_verdict} size="sm" />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap font-mono text-2xs text-slate-500">
                      {res.reflection_rounds > 0 ? `${res.reflection_rounds} loops` : 'Direct'}
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-2xs max-w-xs">{res.rationale}</td>
                  </tr>
                ))
              ) : (
                testCases.map((tc) => (
                  <tr key={tc.id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 whitespace-nowrap font-mono text-2xs text-slate-400">
                      {tc.id}
                    </td>
                    <td className="px-4 py-3 max-w-sm font-medium text-slate-900">{tc.claim}</td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <StatusBadge verdict={tc.ground_truth_verdict} size="sm" />
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-2xs bg-slate-100 text-slate-700 px-2 py-0.5 rounded">
                        {tc.category}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-2xs max-w-xs">{tc.rationale}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
