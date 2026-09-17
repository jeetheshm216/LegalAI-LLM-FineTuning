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
  // If envUrl points to localhost/127.0.0.1, but client browser is accessing via a LAN IP or domain
  // (e.g. 192.168.x.x, domain.com), do NOT route to client's own localhost. Route through relative path ('')
  // which uses Vite's proxy directly to the backend.
  if (typeof window !== 'undefined' && window.location && window.location.hostname) {
    const isLocalEnv = envUrl.includes('localhost') || envUrl.includes('127.0.0.1');
    const isRemoteClient = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
    if (isLocalEnv && isRemoteClient) {
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

      while (true) {
        let readResult;
        try {
          readResult = await reader.read();
        } catch (streamErr) {
          if (isCompleted) {
            return; // Stream closed normally after complete payload
          }
          throw streamErr;
        }

        const { value, done } = readResult;
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop(); // Retain incomplete line

        let currentEvent = 'message';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;

          if (trimmed.startsWith('event:')) {
            currentEvent = trimmed.slice(6).trim();
          } else if (trimmed.startsWith('data:')) {
            const rawData = trimmed.slice(5).trim();
            try {
              const parsed = JSON.parse(rawData);
              if (currentEvent === 'token') {
                if (parsed.token !== undefined) {
                  onToken?.(parsed.token);
                }
              } else if (currentEvent === 'complete') {
                isCompleted = true;
                onComplete?.(parsed);
                try { await reader.cancel(); } catch {}
                return;
              }
            } catch (jsonErr) {
              console.warn('Failed to parse SSE payload:', rawData);
            }
          }
        }
      }
    } catch (err) {
      if (err.name === 'AbortError' || isCompleted) {
        return;
      }
      onError?.(err);
    }
  }
};
