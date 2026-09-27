import React from 'react';
import { Split, Search, Scale, Eye, CheckCircle2, RotateCw } from 'lucide-react';

export function PipelineVisualizer({ activeStep, reflectionRound, logs }) {
  const steps = [
    { id: 'claim_extractor', label: '1. Claim Extractor', icon: Split, desc: 'Deconstructs text into checkable claims' },
    { id: 'evidence_retriever', label: '2. Evidence Retriever', icon: Search, desc: 'Tavily live web & RAG archive search' },
    { id: 'verdict_judge', label: '3. Verdict Judge', icon: Scale, desc: 'Dual-sided balance & IFCN scoring' },
    { id: 'critic', label: '4. Critic (Reflection)', icon: Eye, desc: 'Audits bias & requests counter-evidence' },
    { id: 'finalize', label: '5. MCP Finalizer', icon: CheckCircle2, desc: 'Persists claims & prepares digest' },
  ];

  const getStepState = (stepId) => {
    if (!activeStep) return 'idle';
    if (activeStep === 'completed') return 'completed';
    if (activeStep === stepId) return 'active';

    const order = ['claim_extractor', 'evidence_retriever', 'verdict_judge', 'critic', 'finalize'];
    const activeIndex = order.indexOf(activeStep);
    const stepIndex = order.indexOf(stepId);

    if (stepIndex < activeIndex) return 'completed';
    return 'pending';
  };

  return (
    <div className="bg-white border border-slate-200 rounded-sm p-5 mb-6 shadow-xs">
      <div className="flex items-center justify-between mb-4 border-b border-slate-100 pb-3">
        <div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-800 flex items-center gap-2">
            <span>LangGraph Multi-Agent Pipeline</span>
            {reflectionRound > 0 && (
              <span className="inline-flex items-center gap-1 text-xs bg-amber-700 text-white px-2 py-0.5 rounded font-mono font-semibold">
                <RotateCw className="w-3 h-3 animate-spin" />
                Reflection Round {reflectionRound}
              </span>
            )}
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">Sequential execution with reflection loop back to Evidence Retriever when deeper verification is required</p>
        </div>
      </div>

      {/* Steps Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {steps.map((s) => {
          const Icon = s.icon;
          const state = getStepState(s.id);
          
          let cardBg = 'bg-slate-50 border-slate-200 text-slate-600';
          let iconBg = 'bg-slate-200 text-slate-700';

          if (state === 'active') {
            cardBg = 'bg-slate-900 border-slate-900 text-white shadow-sm';
            iconBg = 'bg-emerald-600 text-white';
          } else if (state === 'completed') {
            cardBg = 'bg-slate-100 border-slate-300 text-slate-800';
            iconBg = 'bg-slate-800 text-white';
          }

          return (
            <div key={s.id} className={`border rounded-sm p-3 transition-all ${cardBg}`}>
              <div className="flex items-center gap-2 mb-1.5">
                <div className={`w-7 h-7 rounded-sm flex items-center justify-center shrink-0 ${iconBg}`}>
                  <Icon className="w-4 h-4" />
                </div>
                <span className="text-xs font-bold tracking-tight">{s.label}</span>
              </div>
              <p className={`text-2xs leading-snug ${state === 'active' ? 'text-slate-300' : 'text-slate-500'}`}>
                {s.desc}
              </p>
            </div>
          );
        })}
      </div>

      {/* Step Event Logs */}
      {logs && logs.length > 0 && (
        <div className="mt-4 pt-3 border-t border-slate-100">
          <span className="text-2xs font-bold uppercase tracking-wider text-slate-500 block mb-2">Agent Execution Log:</span>
          <div className="max-h-36 overflow-y-auto space-y-1.5 font-mono text-2xs bg-slate-900 text-slate-200 p-3 rounded-sm">
            {logs.map((log, idx) => (
              <div key={idx} className="flex items-start gap-2">
                <span className="text-slate-500 shrink-0">[{log.time}]</span>
                <span className="text-emerald-400 font-bold uppercase shrink-0">{log.node}:</span>
                <span className="text-slate-200">{log.description}</span>
                {log.round > 0 && <span className="text-amber-400 shrink-0">(R{log.round})</span>}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
