import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/apiClient';

export function useDigestController() {
  const [digests, setDigests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedTopic, setSelectedTopic] = useState('Technology');
  const [dateStr, setDateStr] = useState(new Date().toISOString().split('T')[0]);
  const [activeDigest, setActiveDigest] = useState(null);
  const [error, setError] = useState(null);

  const fetchDigests = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.listDigests(20);
      setDigests(data);
      if (data.length > 0 && !activeDigest) {
        setActiveDigest(data[0]);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [activeDigest]);

  useEffect(() => {
    fetchDigests();
  }, [fetchDigests]);

  const generateNewDigest = async () => {
    setGenerating(true);
    setError(null);
    try {
      const newDigest = await apiClient.generateDigest({
        topic: selectedTopic,
        date_str: dateStr
      });
      setDigests((prev) => [newDigest, ...prev]);
      setActiveDigest(newDigest);
    } catch (err) {
      setError(err.message);
    } finally {
      setGenerating(false);
    }
  };

  return {
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
    fetchDigests,
    generateNewDigest
  };
}
