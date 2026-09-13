import { INITIAL_CONVERSATIONS, MOCK_LEGAL_RESPONSES } from '../mock/mockAI';

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

  // Stream mock tokens
  sendMessageStream: ({ convId, content, onToken, onComplete, signal }) => {
    const matched = content.toLowerCase().includes("bail") 
      ? MOCK_LEGAL_RESPONSES[0] 
      : MOCK_LEGAL_RESPONSES[1];

    const fullResponse = matched.content;
    const words = fullResponse.split(" ");
    let currentText = "";
    let index = 0;

    const interval = setInterval(() => {
      if (signal?.aborted) {
        clearInterval(interval);
        return;
      }

      if (index < words.length) {
        currentText += (index === 0 ? "" : " ") + words[index];
        onToken(currentText);
        index++;
      } else {
        clearInterval(interval);
        const aiMessage = {
          id: `msg-${Date.now()}`,
          role: "assistant",
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          content: fullResponse,
          reliability: matched.reliability,
          reliabilityLabel: matched.reliabilityLabel,
          sources: matched.sources
        };

        // Persist message in conversation store
        conversationsStore = conversationsStore.map(c => {
          if (c.id === convId) {
            return {
              ...c,
              updatedAt: "Just now",
              messages: [...c.messages, aiMessage]
            };
          }
          return c;
        });

        onComplete(aiMessage);
      }
    }, 45); // Calm stream speed without lag

    return () => clearInterval(interval);
  },

  // Contextual Ask AI on selected text (§15.7)
  askContextualAI: async ({ selectedText, question, conversationContext }) => {
    await new Promise(r => setTimeout(r, 600)); // Brief realistic delay

    const followUpAnswers = [
      `Regarding the excerpt: "${selectedText.slice(0, 70)}..."\n\nUnder applicable procedural rules, this stipulation requires strict adherence within the statutory timeline. If contested by opposing counsel, an interlocutory affidavit specifying lack of willful default should be filed immediately.`,
      `In direct reference to the selected clause: "${selectedText.slice(0, 70)}..."\n\nJudicial precedent confirms that where ambiguity exists, the interpretation favoring preservation of existing operational status quo takes precedence before the Commercial Division.`
    ];

    return {
      id: `ctx-${Date.now()}`,
      role: "assistant",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      content: followUpAnswers[Math.floor(Math.random() * followUpAnswers.length)],
      sources: [
        {
          id: "ctx-src-1",
          type: "statute",
          title: "High Court Commercial Division Practice Directions",
          reference: "Direction 14(A)",
          excerpt: "Treatment of interlocutory status quo covenants."
        }
      ]
    };
  }
};
