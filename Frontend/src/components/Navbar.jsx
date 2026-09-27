import React from 'react';
import { ShieldCheck, FileText, Database, CheckCircle2, Settings } from 'lucide-react';

export function Navbar({ activeRoute, setActiveRoute, onOpenSettings }) {
  const navItems = [
    { id: 'factcheck', label: 'Fact-Check Pipeline', icon: ShieldCheck },
    { id: 'digest', label: 'Daily Digest', icon: FileText },
    { id: 'archive', label: 'Claims Archive & Sources', icon: Database },
    { id: 'eval', label: 'Benchmark Evaluation', icon: CheckCircle2 },
  ];

  return (
    <header className="bg-slate-900 border-b border-slate-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 bg-slate-800 border border-slate-700 rounded-sm flex items-center justify-center">
              <ShieldCheck className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold tracking-tight text-lg text-white">VERITAS</span>
                <span className="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 uppercase font-mono">
                  LangGraph Agent
                </span>
              </div>
              <p className="text-xs text-slate-400 font-normal">Misinformation Detection & Dual-Sided Fact Verification</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="hidden md:flex space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeRoute === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveRoute(item.id)}
                  className={`flex items-center gap-2 px-3.5 py-2 text-sm font-medium rounded-sm transition-colors ${
                    isActive
                      ? 'bg-slate-800 text-white border-b-2 border-emerald-500'
                      : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                  }`}
                >
                  <Icon className="w-4 h-4 text-slate-400" />
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Settings Trigger */}
          <div className="flex items-center gap-2">
            <button
              onClick={onOpenSettings}
              className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-sm border border-slate-800 transition-colors"
              title="System Configuration & API Keys"
            >
              <Settings className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        <div className="md:hidden flex overflow-x-auto space-x-1 py-2 border-t border-slate-800">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeRoute === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveRoute(item.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-sm whitespace-nowrap ${
                  isActive ? 'bg-slate-800 text-white' : 'text-slate-400 hover:text-white'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
