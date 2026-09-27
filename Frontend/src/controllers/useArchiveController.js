import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/apiClient';

export function useArchiveController() {
  const [claims, setClaims] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedVerdict, setSelectedVerdict] = useState('All');
  const [activeTab, setActiveTab] = useState('claims'); // 'claims' | 'sources'
  const [error, setError] = useState(null);

  const fetchClaims = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getSavedClaims(searchQuery, selectedVerdict);
      setClaims(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [searchQuery, selectedVerdict]);

  const fetchSources = useCallback(async () => {
    try {
      const data = await apiClient.getTrustedSources();
      setSources(data);
    } catch (err) {
      console.error('Failed to fetch sources:', err);
    }
  }, []);

  useEffect(() => {
    fetchClaims();
  }, [fetchClaims]);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  return {
    claims,
    sources,
    loading,
    searchQuery,
    setSearchQuery,
    selectedVerdict,
    setSelectedVerdict,
    activeTab,
    setActiveTab,
    error,
    refreshClaims: fetchClaims
  };
}
