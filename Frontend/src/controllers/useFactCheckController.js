import { useState, useCallback } from 'react';
import { apiClient } from '../api/apiClient';

export const SAMPLE_QUERIES = [
  {
    title: 'Health: Hot Water Cure Myth',
    query: 'Is it true that drinking hot water cures viral infections?'
  },
  {
    title: 'Forwarded Social Media Hoax',
    query: 'Fact-check this forwarded message: UNESCO officially declared the national anthem of India as the best anthem in the world.'
  },
  {
    title: 'Astronomy: JWST Water Discovery',
    query: 'Did the James Webb Space Telescope confirm the presence of water vapor in the atmosphere of exoplanet WASP-96b?'
  },
  {
    title: 'Technology & Health: 5G Towers',
    query: 'Forwarded post claims 5G cellular radiation weakens human immunity and triggers respiratory diseases.'
  },
  {
    title: 'Unsubstantiated Rumor (Guardrail Test)',
    query: 'Classified alien wreckage was extracted from an unnamed Pacific trench by a covert submarine yesterday.'
  }
];

export function useFactCheckController() {
  const [inputText, setInputText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [activeStep, setActiveStep] = useState(null); // 'claim_extractor', 'evidence_retriever', 'verdict_judge', 'critic', 'finalize'
  const [reflectionRound, setReflectionRound] = useState(0);
  const [logs, setLogs] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [maxReflections, setMaxReflections] = useState(2);

  const handleSelectSample = (query) => {
    setInputText(query);
    setError(null);
  };

  const runAnalysis = useCallback(async () => {
    if (!inputText.trim() || isAnalyzing) return;

    setIsAnalyzing(true);
    setError(null);
    setLogs([]);
    setResult(null);
    setActiveStep('claim_extractor');
    setReflectionRound(0);

    const payload = {
      text: inputText.trim(),
      check_live_web: true,
      max_reflections: maxReflections
    };

    apiClient.streamFactCheck(
      payload,
      (chunk) => {
        if (chunk.event === 'started') {
          setActiveStep('claim_extractor');
        } else if (chunk.event === 'node_update') {
          setActiveStep(chunk.node);
          if (chunk.reflection_round !== undefined) {
            setReflectionRound(chunk.reflection_round);
          }
          setLogs((prev) => [
            ...prev,
            {
              node: chunk.node,
              description: chunk.description,
              details: chunk.details,
              round: chunk.reflection_round || 0,
              time: new Date().toLocaleTimeString()
            }
          ]);
        } else if (chunk.event === 'finished') {
          setActiveStep('completed');
          setResult(chunk.data);
        } else if (chunk.event === 'error') {
          setError(chunk.message);
        }
      },
      (err) => {
        console.error('Fact check streaming failed:', err);
        setError(err.message || 'Analysis failed. Please try again.');
        setIsAnalyzing(false);
      },
      () => {
        setIsAnalyzing(false);
      }
    );
  }, [inputText, isAnalyzing, maxReflections]);

  const clearResults = () => {
    setResult(null);
    setLogs([]);
    setActiveStep(null);
    setError(null);
  };

  return {
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
  };
}
