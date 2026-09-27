import { useState, useEffect, useCallback } from 'react';
import { apiClient } from '../api/apiClient';

export function useEvalController() {
  const [testCases, setTestCases] = useState([]);
  const [report, setReport] = useState(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  const fetchDataset = useCallback(async () => {
    try {
      const data = await apiClient.getEvalDataset();
      setTestCases(data);
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    fetchDataset();
  }, [fetchDataset]);

  const runBenchmark = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const res = await apiClient.runEvalBenchmark();
      setReport(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsRunning(false);
    }
  };

  return {
    testCases,
    report,
    isRunning,
    error,
    runBenchmark
  };
}
