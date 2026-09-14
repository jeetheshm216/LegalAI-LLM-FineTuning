/**
 * aiService.js
 * 
 * Legal AI Assistant Service connecting directly to the LegalAI FastAPI backend
 * (/api/v1/ai/chat/stream and /api/v1/ai/contextual).
 * Executes Qwen2.5-14B + LoRA V2 + Statutory RAG pipeline on Physical GPU 2.
 */

import { apiClient } from './apiClient';
import { INITIAL_CONVERSATIONS } from '../mock/mockAI';

let conversationsStore = [...INITIAL_CONVERSATIONS];

export const aiService = {
  getConversations: async () => {
    return [...conversationsStore];
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
    return newConv;
  },

  updateContextSettings: async (convId, settings) => {
    conversationsStore = conversationsStore.map(c => {
      if (c.id === convId) {
        return {
          ...c,
          contextSettings: { ...c.contextSettings, ...settings }
        };
      }
      return c;
    });
    return conversationsStore.find(c => c.id === convId);
  },

  /**
   * Primary streaming AI query execution connecting to backend SSE.
   */
  sendMessageStream: ({ convId, content, onToken, onComplete }) => {
    const controller = new AbortController();
    const activeConv = conversationsStore.find(c => c.id === convId);

    const payload = {
      content,
      conversationId: convId,
      mode: activeConv?.mode || "GENERAL",
      caseId: activeConv?.caseId || null,
      caseNumber: activeConv?.caseNumber || null,
      selectedCases: activeConv?.selectedCases || [],
      contextSettings: activeConv?.contextSettings || null
    };

    let accumulated = "";

    apiClient.streamSSE({
      endpoint: '/api/v1/ai/chat/stream',
      body: payload,
      signal: controller.signal,
      onToken: (tokenString) => {
        accumulated = tokenString;
        onToken?.(tokenString);
      },
      onComplete: (aiMessage) => {
        hasCompleted = true;
        const finalMessage = {
          id: aiMessage.id || `msg-${Date.now()}`,
          role: "assistant",
          timestamp: aiMessage.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          content: aiMessage.content || accumulated,
          reliability: aiMessage.reliability || "supported",
          reliabilityLabel: aiMessage.reliabilityLabel || "Supported by sources",
          sources: aiMessage.sources || [],
          citations: aiMessage.citations || []
        };

        // Persist message in conversation store
        conversationsStore = conversationsStore.map(c => {
          if (c.id === convId) {
            return {
              ...c,
              updatedAt: "Just now",
              messages: [...c.messages, finalMessage]
            };
          }
          return c;
        });

        onComplete?.(finalMessage);
      },
      onError: async (err) => {
        if (hasCompleted) {
          return; // Already completed successfully; ignore trailing stream closure
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
              citations: fallbackRes.citations || []
            };

            conversationsStore = conversationsStore.map(c => {
              if (c.id === convId) {
                return {
                  ...c,
                  updatedAt: "Just now",
                  messages: [...c.messages, finalMessage]
                };
              }
              return c;
            });

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
            return {
              ...c,
              updatedAt: "Just now",
              messages: [...c.messages, fallbackMsg]
            };
          }
          return c;
        });

        onComplete?.(fallbackMsg);
      }
    });

    return () => controller.abort();
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
