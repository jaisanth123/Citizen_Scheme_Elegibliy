const BASE_URL = '/api';

export const apiClient = {
  async factCheck(payload) {
    const res = await fetch(`${BASE_URL}/fact-check`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Fact check error: ${res.statusText}`);
    return res.json();
  },

  async streamFactCheck(payload, onEvent, onError, onDone) {
    try {
      const response = await fetch(`${BASE_URL}/fact-check/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`Stream error: ${response.statusText}`);

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.trim()) {
            try {
              const data = JSON.parse(line);
              onEvent(data);
            } catch (err) {
              console.warn('Could not parse SSE event chunk:', line);
            }
          }
        }
      }
      onDone();
    } catch (err) {
      onError(err);
    }
  },

  async generateDigest(payload) {
    const res = await fetch(`${BASE_URL}/digest/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Digest generation error: ${res.statusText}`);
    return res.json();
  },

  async listDigests(limit = 20) {
    const res = await fetch(`${BASE_URL}/digest/list?limit=${limit}`);
    if (!res.ok) throw new Error(`Failed to list digests: ${res.statusText}`);
    return res.json();
  },

  getDigestExportUrl(digestId) {
    return `${BASE_URL}/digest/${digestId}/export`;
  },

  async getSavedClaims(query = '', verdict = '', limit = 50) {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (verdict && verdict !== 'All') params.append('verdict', verdict);
    params.append('limit', limit.toString());

    const res = await fetch(`${BASE_URL}/archive/claims?${params.toString()}`);
    if (!res.ok) throw new Error(`Failed to fetch claims: ${res.statusText}`);
    return res.json();
  },

  getClaimExportUrl(claimId) {
    return `${BASE_URL}/archive/claims/${claimId}/export`;
  },

  async getTrustedSources() {
    const res = await fetch(`${BASE_URL}/archive/sources`);
    if (!res.ok) throw new Error(`Failed to fetch trusted sources: ${res.statusText}`);
    return res.json();
  },

  async getEvalDataset() {
    const res = await fetch(`${BASE_URL}/eval/dataset`);
    if (!res.ok) throw new Error(`Failed to fetch eval dataset: ${res.statusText}`);
    return res.json();
  },

  async runEvalBenchmark() {
    const res = await fetch(`${BASE_URL}/eval/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(`Evaluation benchmark error: ${res.statusText}`);
    return res.json();
  },

  async getSystemConfig() {
    const res = await fetch(`${BASE_URL}/config`);
    if (!res.ok) throw new Error(`Failed to get system config: ${res.statusText}`);
    return res.json();
  },

  async updateSystemConfig(payload) {
    const res = await fetch(`${BASE_URL}/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`Failed to update config: ${res.statusText}`);
    return res.json();
  }
};
