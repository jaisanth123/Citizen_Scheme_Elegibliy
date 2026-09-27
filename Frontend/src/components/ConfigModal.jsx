import React, { useState, useEffect } from 'react';
import { X, Key, Check } from 'lucide-react';
import { apiClient } from '../api/apiClient';

export function ConfigModal({ isOpen, onClose }) {
  const [config, setConfig] = useState(null);
  const [tavilyKey, setTavilyKey] = useState('');
  const [saving, setSaving] = useState(false);
  const [savedMsg, setSavedMsg] = useState(null);

  useEffect(() => {
    if (isOpen) {
      apiClient.getSystemConfig().then(setConfig).catch(console.error);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSavedMsg(null);
    try {
      await apiClient.updateSystemConfig({
        tavily_api_key: tavilyKey.trim() || undefined,
      });
      setSavedMsg('Settings updated successfully.');
      const updated = await apiClient.getSystemConfig();
      setConfig(updated);
      setTavilyKey('');
    } catch (err) {
      alert(`Save failed: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/70 flex items-center justify-center p-4">
      <div className="bg-white border border-slate-300 rounded-sm shadow-xl max-w-md w-full overflow-hidden">
        {/* Header */}
        <div className="bg-slate-900 text-white px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-emerald-400" />
            <h3 className="text-sm font-bold tracking-tight">System & API Configuration</h3>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {config && (
            <div className="mb-5 bg-slate-50 border border-slate-200 p-3 rounded-sm space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Tavily Web Search:</span>
                <span className={`font-semibold ${config.tavily_configured ? 'text-emerald-700' : 'text-slate-600'}`}>
                  {config.tavily_configured ? 'Configured & Active' : 'Fallback Search Engine Active'}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Active LLM Engine:</span>
                <span className="font-semibold text-slate-800">{config.llm_provider.toUpperCase()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">RAG Trusted Sources:</span>
                <span className="font-mono text-slate-800 font-bold">{config.database_stats?.trusted_sources || 15} authoritative domains</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">MCP Saved Claims:</span>
                <span className="font-mono text-slate-800 font-bold">{config.database_stats?.total_claims || 0} claims in DB</span>
              </div>
            </div>
          )}

          <form onSubmit={handleSave}>
            <div className="mb-4">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-700 mb-1">
                Tavily API Key (Optional)
              </label>
              <input
                type="password"
                placeholder="tvly-..."
                value={tavilyKey}
                onChange={(e) => setTavilyKey(e.target.value)}
                className="w-full text-xs font-mono px-3 py-2 border border-slate-300 rounded-sm focus:outline-hidden focus:border-slate-800"
              />
              <p className="text-2xs text-slate-500 mt-1">
                Leave blank to utilize the built-in intelligent search index fallback without requiring external API keys.
              </p>
            </div>

            {savedMsg && (
              <div className="mb-4 bg-emerald-50 border border-emerald-200 text-emerald-800 px-3 py-2 text-xs rounded-sm flex items-center gap-2">
                <Check className="w-4 h-4 text-emerald-700" />
                <span>{savedMsg}</span>
              </div>
            )}

            <div className="flex justify-end gap-2 pt-2 border-t border-slate-200">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-xs text-slate-700 hover:bg-slate-100 rounded-sm border border-slate-300 transition-colors"
              >
                Close
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 text-xs bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-sm transition-colors"
              >
                {saving ? 'Updating...' : 'Save Configuration'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
