import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { ConfigModal } from './components/ConfigModal';
import { FactCheckView } from './routes/FactCheckView';
import { DigestView } from './routes/DigestView';
import { ArchiveView } from './routes/ArchiveView';
import { EvaluationView } from './routes/EvaluationView';
import { Shield } from 'lucide-react';

export function App() {
  const [activeRoute, setActiveRoute] = useState('factcheck');
  const [isConfigOpen, setIsConfigOpen] = useState(false);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 flex flex-col font-sans selection:bg-slate-900 selection:text-white">
      {/* Masthead Navbar */}
      <Navbar
        activeRoute={activeRoute}
        setActiveRoute={setActiveRoute}
        onOpenSettings={() => setIsConfigOpen(true)}
      />

      {/* Main View Router */}
      <main className="flex-1">
        {activeRoute === 'factcheck' && <FactCheckView />}
        {activeRoute === 'digest' && <DigestView />}
        {activeRoute === 'archive' && <ArchiveView />}
        {activeRoute === 'eval' && <EvaluationView />}
      </main>

      {/* Configuration & Settings Modal */}
      <ConfigModal
        isOpen={isConfigOpen}
        onClose={() => setIsConfigOpen(false)}
      />

      {/* Professional Footer */}
      <footer className="bg-slate-900 text-slate-400 border-t border-slate-800 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-wrap items-center justify-between gap-4 text-xs">
          <div className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-emerald-400" />
            <span className="font-semibold text-slate-200">VERITAS Pipeline</span>
            <span>— LangGraph Multi-Agent Fact Verification System</span>
          </div>

          <div className="flex items-center gap-4 text-2xs text-slate-500 font-mono">
            <span>IFCN Standards Compliant</span>
            <span>•</span>
            <span>Tavily Live Web Search</span>
            <span>•</span>
            <span>Model Context Protocol (MCP)</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
