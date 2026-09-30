/**
 * apiClient.js
 * 
 * Centralized API client for LegalAI Frontend.
 * Connects to the LegalAI FastAPI backend on port 8008.
 * Supports standard JSON REST calls, multipart FormData, Bearer auth tokens,
 * and Server-Sent Events (SSE) streaming.
 */

function getApiBaseUrl() {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (!envUrl || envUrl.trim() === '') {
    return '';
  }
  // When running in a browser, if envUrl points to localhost or 127.0.0.1,
  // return '' (relative path) so requests use the same host & port (e.g. Vite on 5173),
  // which proxies /api to port 8008 on the host. This prevents 'Failed to fetch'
  // when port 8008 is not forwarded or directly accessible from the client machine.
  if (typeof window !== 'undefined') {
    if (envUrl.includes('localhost') || envUrl.includes('127.0.0.1')) {
      return '';
    }
  }
  return envUrl.replace(/\/+$/, '');
}

const API_BASE_URL = getApiBaseUrl();

class ApiError extends Error {
  constructor(message, status, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

function getAuthToken() {
  try {
    return localStorage.getItem('legalai_auth_token') || null;
  } catch {
    return null;
  }
}

async function request(endpoint, options = {}) {
  const url = `${getApiBaseUrl()}${endpoint}`;
  const headers = {
    Accept: 'application/json',
    ...(options.headers || {})
  };

  const token = getAuthToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Auto-set Content-Type for JSON payloads unless already specified (e.g. multipart)
  if (options.body && !(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers
    });

    if (!response.ok) {
      let errorMessage = `Request failed with status ${response.status}`;
      let errorData = null;
      try {
        errorData = await response.json();
        if (errorData?.detail) {
          errorMessage = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        errorMessage = response.statusText || errorMessage;
      }
      throw new ApiError(errorMessage, response.status, errorData);
    }

    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (err) {
    if (err instanceof ApiError) {
      throw err;
    }
    throw new ApiError(err.message || 'Network request failed', 0, err);
  }
}

export const apiClient = {
  get: (endpoint, options = {}) => 
    request(endpoint, { ...options, method: 'GET' }),

  post: (endpoint, body, options = {}) => 
    request(endpoint, {
      ...options,
      method: 'POST',
      body: body instanceof FormData ? body : JSON.stringify(body)
    }),

  patch: (endpoint, body, options = {}) => 
    request(endpoint, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(body)
    }),

  delete: (endpoint, options = {}) => 
    request(endpoint, { ...options, method: 'DELETE' }),

  uploadFile: (endpoint, formData, options = {}) => 
    request(endpoint, {
      ...options,
      method: 'POST',
      body: formData
    }),

  /**
   * Connects to a Server-Sent Events (SSE) streaming endpoint using native fetch.
   */
  streamSSE: async ({ endpoint, body, onToken, onComplete, onError, signal }) => {
    const url = `${getApiBaseUrl()}${endpoint}`;
    const token = getAuthToken();
    const headers = {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream'
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    let isCompleted = false;
    let accumulatedToken = '';
    let lastCompletePayload = null;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        signal
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new ApiError(`SSE stream error: ${response.status}`, response.status, errorText);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let currentEvent = 'message';
      let currentData = '';

      const processLine = (line) => {
        const trimmed = line.trim();
        if (!trimmed) {
          // Empty line indicates dispatch of current event block
          if (currentData) {
            try {
              const parsed = JSON.parse(currentData);
              if (currentEvent === 'token') {
                if (parsed.token !== undefined) {
                  accumulatedToken = parsed.token;
                  onToken?.(parsed.token);
                }
              } else if (currentEvent === 'complete') {
                isCompleted = true;
                lastCompletePayload = parsed;
                onComplete?.(parsed);
              }
            } catch (jsonErr) {
              console.warn('Failed to parse SSE payload:', currentData);
            }
          }
          currentEvent = 'message';
          currentData = '';
          return;
        }

        if (trimmed.startsWith('event:')) {
          currentEvent = trimmed.slice(6).trim();
        } else if (trimmed.startsWith('data:')) {
          const lineData = trimmed.slice(5).trim();
          currentData = currentData ? (currentData + '\n' + lineData) : lineData;
        }
      };

      while (true) {
        let readResult;
        try {
          readResult = await reader.read();
        } catch (streamErr) {
          if (isCompleted) {
            return;
          }
          throw streamErr;
        }

        const { value, done } = readResult;
        if (done) {
          // Flush any remaining buffer when stream finishes
          if (buffer.trim()) {
            const finalLines = buffer.split('\n');
            for (const fl of finalLines) {
              processLine(fl);
            }
            processLine(''); // Dispatch final event if pending
          } else if (currentData) {
            processLine(''); // Dispatch final pending data
          }
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Retain incomplete line

        for (const line of lines) {
          processLine(line);
          if (isCompleted) {
            try { await reader.cancel(); } catch {}
            return;
          }
        }
      }

      // Stream closed by server normally. Ensure completion is triggered!
      if (!isCompleted) {
        isCompleted = true;
        onComplete?.(lastCompletePayload || {
          id: `msg-${Date.now()}`,
          role: 'assistant',
          content: accumulatedToken,
          reliability: 'supported',
          reliabilityLabel: 'Completed',
          query_type: 'GENERATION_COMPLETE'
        });
      }
    } catch (err) {
      if (err.name === 'AbortError' || isCompleted) {
        return;
      }
      onError?.(err);
    }
  }
};
