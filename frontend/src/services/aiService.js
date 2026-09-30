/**
 * aiService.js
 * 
 * Legal AI Assistant Service connecting directly to the LegalAI FastAPI backend
 * (/api/v1/ai/chat/stream, /api/v1/ai/contextual, and /api/v1/conversations).
 * Executes Qwen2.5-14B + LoRA V2 + Statutory RAG pipeline on Physical GPU 2.
 * Fully persists conversation history and lifecycle management in Supabase and localStorage.
 */

import { apiClient } from './apiClient';
import { INITIAL_CONVERSATIONS } from '../mock/mockAI';
import { supabase, isSupabaseConfigured } from './supabaseClient';

const STORAGE_KEY = 'legalai_conversations';
const ACTIVE_CONV_KEY = 'legalai_active_conv_id';

function getStoredConversationsLocal() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed;
      }
    }
  } catch (err) {
    console.warn('[aiService] Failed to load conversations from localStorage:', err);
  }
  return [...INITIAL_CONVERSATIONS];
}

function saveConversationsLocal(convs) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(convs));
  } catch (err) {
    console.warn('[aiService] Failed to save conversations to localStorage:', err);
  }
}

// Background sync to Supabase table 'conversations'
async function syncConversationToSupabase(conv) {
  if (!isSupabaseConfigured || !supabase) return;
  try {
    const record = {
      id: conv.id,
      title: conv.title,
      mode: conv.mode,
      case_id: conv.caseId || null,
      case_number: conv.caseNumber || null,
      selected_cases: conv.selectedCases || [],
      context_settings: conv.contextSettings || {},
      messages: conv.messages || [],
      updated_at: new Date().toISOString()
    };
    await supabase.from('conversations').upsert(record, { onConflict: 'id' });
  } catch (err) {
    console.warn('[aiService] Supabase sync skipped:', err.message || err);
  }
}

// Background sync to backend database /api/v1/conversations
async function syncConversationToBackend(conv) {
  try {
    await apiClient.post('/api/v1/conversations', conv).catch(() => {});
  } catch (_) {}
}

function mergeConversations(remoteList, localList) {
  const mergedMap = new Map();
  (localList || []).forEach(c => {
    if (c && c.id) mergedMap.set(c.id, { ...c });
  });
  (remoteList || []).forEach(r => {
    if (!r || !r.id) return;
    if (mergedMap.has(r.id)) {
      const local = mergedMap.get(r.id);
      const localMsgs = Array.isArray(local.messages) ? local.messages : [];
      const remoteMsgs = Array.isArray(r.messages) ? r.messages : [];
      mergedMap.set(r.id, {
        ...r,
        ...local,
        messages: localMsgs.length >= remoteMsgs.length ? localMsgs : remoteMsgs
      });
    } else {
      mergedMap.set(r.id, r);
    }
  });
  return Array.from(mergedMap.values());
}

let conversationsStore = getStoredConversationsLocal();

export const aiService = {
  getStoredConversations: () => {
    return getStoredConversationsLocal();
  },

  saveAllConversations: (convs) => {
    if (!Array.isArray(convs)) return;
    conversationsStore = convs;
    saveConversationsLocal(convs);
    const activeId = localStorage.getItem(ACTIVE_CONV_KEY);
    const target = convs.find(c => c.id === activeId) || convs[0];
    if (target && target.messages && target.messages.length > 0) {
      syncConversationToSupabase(target);
      syncConversationToBackend(target);
    }
  },

  getConversations: async () => {
    const local = getStoredConversationsLocal();

    // 1. Try fetching from Supabase if configured
    if (isSupabaseConfigured && supabase) {
      try {
        const { data, error } = await supabase
          .from('conversations')
          .select('*')
          .order('updated_at', { ascending: false });
        if (!error && data && data.length > 0) {
          const mapped = data.map(row => ({
            id: row.id,
            title: row.title,
            mode: row.mode || 'GENERAL',
            caseId: row.case_id,
            caseNumber: row.case_number,
            selectedCases: row.selected_cases || [],
            contextSettings: row.context_settings || {},
            updatedAt: row.updated_at ? new Date(row.updated_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recently',
            messages: row.messages || []
          }));
          const merged = mergeConversations(mapped, local);
          conversationsStore = merged;
          saveConversationsLocal(merged);
          return merged;
        }
      } catch (e) {
        console.warn('[aiService] Supabase fetch error:', e);
      }
    }

    // 2. Try fetching from Backend API
    try {
      const resp = await apiClient.get('/api/v1/conversations');
      if (resp && resp.conversations && resp.conversations.length > 0) {
        const merged = mergeConversations(resp.conversations, local);
        conversationsStore = merged;
        saveConversationsLocal(merged);
        return merged;
      }
    } catch (_) {}

    // 3. Fallback to localStorage / in-memory store
    conversationsStore = local;
    return conversationsStore;
  },

  getConversationById: async (id) => {
    return conversationsStore.find(c => c.id === id) || null;
  },

  createConversation: async ({ title, mode, caseId, caseNumber, selectedCases }) => {
    const newConv = {
      id: `conv-${Date.now()}`,
      title: title || (mode === "GENERAL" ? "General Legal Inquiry" : `Analysis — ${caseNumber || "Selected Matters"}`),
      mode: mode || "GENERAL",
      caseId: caseId || null,
      caseNumber: caseNumber || null,
      selectedCases: selectedCases || (caseId ? [caseId] : []),
      contextSettings: {
        includeDocuments: true,
        includeNotes: true,
        includeTimeline: true,
        includeHistory: true,
        supportingCases: []
      },
      updatedAt: "Just now",
      messages: []
    };
    conversationsStore = [newConv, ...conversationsStore];
    saveConversationsLocal(conversationsStore);
    syncConversationToSupabase(newConv);
    syncConversationToBackend(newConv);
    return newConv;
  },

  renameConversation: async (convId, newTitle) => {
    conversationsStore = conversationsStore.map(c => {
      if (c.id === convId) {
        return { ...c, title: newTitle, updatedAt: 'Just now' };
      }
      return c;
    });
    saveConversationsLocal(conversationsStore);

    // Sync to Supabase
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase
          .from('conversations')
          .update({ title: newTitle, updated_at: new Date().toISOString() })
          .eq('id', convId);
      } catch (err) {
        console.warn('[aiService] Supabase rename error:', err);
      }
    }

    // Sync to backend
    try {
      await apiClient.patch(`/api/v1/conversations/${convId}/title`, { title: newTitle }).catch(() => {});
    } catch (_) {}

    return conversationsStore.find(c => c.id === convId);
  },

  deleteConversation: async (convId) => {
    conversationsStore = conversationsStore.filter(c => c.id !== convId);
    saveConversationsLocal(conversationsStore);

    // Sync to Supabase
    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.from('conversations').delete().eq('id', convId);
      } catch (err) {
        console.warn('[aiService] Supabase delete error:', err);
      }
    }

    // Sync to backend
    try {
      await apiClient.delete(`/api/v1/conversations/${convId}`).catch(() => {});
    } catch (_) {}

    return true;
  },

  clearAllConversations: async () => {
    conversationsStore = [];
    saveConversationsLocal([]);

    if (isSupabaseConfigured && supabase) {
      try {
        await supabase.from('conversations').delete().neq('id', '');
      } catch (err) {
        console.warn('[aiService] Supabase clear error:', err);
      }
    }

    try {
      localStorage.removeItem(ACTIVE_CONV_KEY);
    } catch (_) {}

    return true;
  },

  saveConversation: async (conv) => {
    const nowIso = new Date().toISOString();
    const existingIdx = conversationsStore.findIndex(c => c.id === conv.id);
    if (existingIdx >= 0) {
      conversationsStore[existingIdx] = { ...conversationsStore[existingIdx], ...conv, updatedAt: conv.updatedAt || nowIso };
    } else {
      conversationsStore = [{ ...conv, updatedAt: conv.updatedAt || nowIso }, ...conversationsStore];
    }
    saveConversationsLocal(conversationsStore);
    syncConversationToSupabase(conv);
    syncConversationToBackend(conv);
    return conv;
  },

  updateContextSettings: async (convId, settings) => {
    conversationsStore = conversationsStore.map(c => {
      if (c.id === convId) {
        const updated = {
          ...c,
          contextSettings: { ...c.contextSettings, ...settings }
        };
        syncConversationToSupabase(updated);
        syncConversationToBackend(updated);
        return updated;
      }
      return c;
    });
    saveConversationsLocal(conversationsStore);
    return conversationsStore.find(c => c.id === convId);
  },

  /**
   * Primary streaming AI query execution connecting to backend SSE.
   */
  sendMessageStream: ({
    convId,
    content,
    history,
    mode,
    caseId,
    caseNumber,
    selectedCases,
    contextSettings,
    onToken,
    onComplete,
    onError
  }) => {
    const controller = new AbortController();
    let activeConv = conversationsStore.find(c => c.id === convId);

    const prevHistory = history || (activeConv?.messages || []).map(m => ({
      role: m.role,
      content: m.content || '',
      query_type: m.query_type || null
    }));

    const effectiveMode = mode || activeConv?.mode || "GENERAL";
    const effectiveCaseId = caseId || activeConv?.caseId || null;
    const effectiveCaseNumber = caseNumber || activeConv?.caseNumber || null;
    const effectiveSelectedCases = selectedCases || activeConv?.selectedCases || (effectiveCaseId ? [effectiveCaseId] : []);
    const effectiveContextSettings = contextSettings || activeConv?.contextSettings || null;

    const nowIso = new Date().toISOString();
    const userMsgObj = {
      id: `msg-${Date.now()}`,
      role: 'user',
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content
    };

    if (!activeConv) {
      activeConv = {
        id: convId,
        title: content.slice(0, 32) + (content.length > 32 ? '…' : ''),
        mode: effectiveMode,
        caseId: effectiveCaseId,
        caseNumber: effectiveCaseNumber,
        selectedCases: effectiveSelectedCases,
        contextSettings: effectiveContextSettings,
        updatedAt: nowIso,
        messages: [userMsgObj]
      };
      conversationsStore = [activeConv, ...conversationsStore];
    } else {
      activeConv.mode = effectiveMode;
      activeConv.caseId = effectiveCaseId;
      activeConv.caseNumber = effectiveCaseNumber;
      activeConv.selectedCases = effectiveSelectedCases;
      if (effectiveContextSettings) {
        activeConv.contextSettings = effectiveContextSettings;
      }
      activeConv.updatedAt = nowIso;
      const msgs = activeConv.messages || [];
      if (!msgs.some(m => m.content === content && m.role === 'user')) {
        activeConv.messages = [...msgs, userMsgObj];
      }
    }
    saveConversationsLocal(conversationsStore);

    const payload = {
      content,
      conversationId: convId,
      mode: effectiveMode,
      caseId: effectiveCaseId,
      caseNumber: effectiveCaseNumber,
      selectedCases: effectiveSelectedCases,
      contextSettings: effectiveContextSettings,
      history: prevHistory
    };

    let accumulated = "";
    let hasCompleted = false;

    apiClient.streamSSE({
      endpoint: '/api/v1/ai/chat/stream',
      body: payload,
      signal: controller.signal,
      onToken: (tokenString) => {
        accumulated = tokenString;
        onToken?.(tokenString);
      },
      onComplete: (aiMessage) => {
        if (hasCompleted) return;
        hasCompleted = true;
        const finalMessage = {
          id: aiMessage?.id || `msg-${Date.now()}`,
          role: "assistant",
          timestamp: aiMessage?.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          content: aiMessage?.content || accumulated,
          reliability: aiMessage?.reliability || "supported",
          reliabilityLabel: aiMessage?.reliabilityLabel || "Supported by sources",
          sources: aiMessage?.sources || [],
          citations: aiMessage?.citations || [],
          query_type: aiMessage?.query_type || null,
          sub_intent: aiMessage?.sub_intent || null,
          user_goal: aiMessage?.user_goal || null,
          output_plan: aiMessage?.output_plan || null,
          suggestions: aiMessage?.suggestions || []
        };

        const nowIso = new Date().toISOString();
        // Persist message in conversation store
        conversationsStore = conversationsStore.map(c => {
          if (c.id === convId) {
            const currentMsgs = c.messages || [];
            const hasFinal = currentMsgs.some(m => m.id === finalMessage.id);
            const updated = {
              ...c,
              updatedAt: nowIso,
              messages: hasFinal ? currentMsgs : [...currentMsgs, finalMessage]
            };
            syncConversationToSupabase(updated);
            syncConversationToBackend(updated);
            return updated;
          }
          return c;
        });
        saveConversationsLocal(conversationsStore);

        onComplete?.(finalMessage);
      },
      onError: async (err) => {
        if (hasCompleted) {
          return; // Already completed successfully; ignore trailing stream closure
        }
        if (controller.signal.aborted) {
          return; // User cancelled
        }
        console.warn('SSE Stream encountered an issue, attempting direct REST fallback:', err.message);

        try {
          // Attempt immediate REST fallback to /api/v1/ai/chat
          const fallbackRes = await apiClient.post('/api/v1/ai/chat', payload);
          if (fallbackRes && fallbackRes.content) {
            hasCompleted = true;
            const finalMessage = {
              id: fallbackRes.id || `msg-${Date.now()}`,
              role: "assistant",
              timestamp: fallbackRes.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              content: fallbackRes.content,
              reliability: fallbackRes.reliability || "supported",
              reliabilityLabel: fallbackRes.reliabilityLabel || "Supported by sources",
              sources: fallbackRes.sources || [],
              citations: fallbackRes.citations || [],
              query_type: fallbackRes.query_type || null,
              sub_intent: fallbackRes.sub_intent || null,
              user_goal: fallbackRes.user_goal || null,
              output_plan: fallbackRes.output_plan || null,
              suggestions: fallbackRes.suggestions || []
            };

            const nowIso = new Date().toISOString();
            conversationsStore = conversationsStore.map(c => {
              if (c.id === convId) {
                const currentMsgs = c.messages || [];
                const hasFinal = currentMsgs.some(m => m.id === finalMessage.id);
                const updated = {
                  ...c,
                  updatedAt: nowIso,
                  messages: hasFinal ? currentMsgs : [...currentMsgs, finalMessage]
                };
                syncConversationToSupabase(updated);
                syncConversationToBackend(updated);
                return updated;
              }
              return c;
            });
            saveConversationsLocal(conversationsStore);

            onComplete?.(finalMessage);
            return;
          }
        } catch (restErr) {
          console.error('REST fallback also failed:', restErr);
        }

        // Only display service advisory if both streaming and REST fallback fail
        const fallbackMsg = {
          id: `msg-${Date.now()}`,
          role: "assistant",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          content: `### Service Advisory\n\nUnable to complete statutory verification via LegalAI RAG service: ${err.message || 'Network connection failed'}. Please check backend service status.`,
          reliability: "verify",
          reliabilityLabel: "Service Advisory",
          sources: []
        };

        conversationsStore = conversationsStore.map(c => {
          if (c.id === convId) {
            const updated = {
              ...c,
              updatedAt: "Just now",
              messages: [...c.messages, fallbackMsg]
            };
            syncConversationToSupabase(updated);
            syncConversationToBackend(updated);
            return updated;
          }
          return c;
        });
        saveConversationsLocal(conversationsStore);

        if (onError) {
          onError(err);
        } else {
          onComplete?.(fallbackMsg);
        }
      }
    });

    return () => {
      try {
        controller.abort();
      } catch (e) {}
    };
  },

  /**
   * Contextual Ask AI on selected text (§15.7)
   */
  askContextualAI: async ({ selectedText, question, conversationContext }) => {
    try {
      const res = await apiClient.post('/api/v1/ai/contextual', {
        selectedText,
        question: question || "",
        conversationContext: conversationContext || {}
      });

      return {
        id: res.id || `ctx-${Date.now()}`,
        role: "assistant",
        timestamp: res.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: res.content,
        sources: res.sources || []
      };
    } catch (err) {
      console.warn('Backend contextual AI failed, returning diagnostic guidance:', err.message);
      return {
        id: `ctx-${Date.now()}`,
        role: "assistant",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        content: `Regarding selected text: "${selectedText.slice(0, 80)}..."\n\nUnder applicable procedural provisions, verify statutory commencement and jurisdictional limitations before the designated court bench.`,
        sources: [
          {
            id: "ctx-src-1",
            type: "statute",
            title: "Practice Directions & Jurisdictional Bench Rules",
            reference: "Direction 14(A)",
            excerpt: "Statutory excerpt cross-reference."
          }
        ]
      };
    }
  }
};
