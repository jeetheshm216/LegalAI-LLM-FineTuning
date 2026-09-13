import { INITIAL_DRAFTS, MOCK_AI_DRAFTING_TEMPLATES } from '../mock/mockDrafting';

let drafts = [...INITIAL_DRAFTS];

export const draftingService = {
  getDrafts: async () => {
    return [...drafts];
  },

  getDraftById: async (id) => {
    return drafts.find(d => d.id === id) || null;
  },

  getDraftsByCase: async (caseId) => {
    return drafts.filter(d => d.caseId === caseId);
  },

  createDraft: async ({ title, documentType, caseId, caseNumber, caseTitle, client, context, instructions }) => {
    const template = MOCK_AI_DRAFTING_TEMPLATES[documentType] || MOCK_AI_DRAFTING_TEMPLATES["Legal Notice"];
    
    // Replace template tokens with real case info if available
    let generatedContent = template
      .replace(/\[Client Name\]/g, client || "Julian Martinez")
      .replace(/\[Opposing Party \/ Company Name\]/g, "Coastal Holdings Limited")
      .replace(/\[Matter Description\]/g, caseTitle || "Maritime Freight Charterparty Dispute")
      .replace(/\[Date\]/g, "14th December 2023")
      .replace(/\[Amount\]/g, "₹55,000")
      .replace(/\[Advocate Name\]/g, "Elena Vance, Advocate");

    if (instructions) {
      generatedContent += `\n\n[Contextual Note: Draft synthesized incorporating advocate directive: "${instructions}"]`;
    }

    const newDraft = {
      id: `draft-${Date.now()}`,
      title: title || `${documentType} — ${caseTitle || "General Matter"}`,
      documentType,
      caseId: caseId || null,
      caseNumber: caseNumber || null,
      caseTitle: caseTitle || "General Matter",
      status: "Draft",
      version: "Version 1",
      wordCount: generatedContent.split(/\s+/).filter(Boolean).length,
      createdAt: new Date().toISOString().replace('T', ' ').substring(0, 16),
      lastModified: "Just now",
      author: "Adv. Elena Vance",
      content: generatedContent,
      versions: [
        {
          id: `v-${Date.now()}`,
          versionNumber: "Version 1",
          timestamp: "Just now",
          author: "Legal AI Studio (Synthesized)",
          summary: `Initial ${documentType} generated with context from ${caseNumber || "general corpus"}.`
        }
      ]
    };

    drafts = [newDraft, ...drafts];
    return newDraft;
  },

  saveDraft: async (id, updatedContent, newSummary) => {
    const draft = drafts.find(d => d.id === id);
    if (!draft) return null;

    const currentVersionCount = draft.versions.length;
    const nextVersionNum = `Version ${currentVersionCount + 1}`;

    const newVersion = {
      id: `v-${Date.now()}`,
      versionNumber: nextVersionNum,
      timestamp: "Just now",
      author: "Adv. Elena Vance",
      summary: newSummary || `Counsel edit & revision (${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})`
    };

    const wordCount = updatedContent.split(/\s+/).filter(Boolean).length;

    drafts = drafts.map(d => {
      if (d.id === id) {
        return {
          ...d,
          content: updatedContent,
          wordCount,
          version: nextVersionNum,
          lastModified: "Just now",
          versions: [newVersion, ...d.versions]
        };
      }
      return d;
    });

    return drafts.find(d => d.id === id);
  },

  // Contextual AI Drafting Action (§ Feature 2)
  aiDraftingAction: async ({ actionType, selectedText, fullDocumentText, customInstruction }) => {
    await new Promise(r => setTimeout(r, 600)); // Realistic processing delay

    const excerpt = selectedText ? selectedText.trim() : fullDocumentText.slice(0, 150);

    switch (actionType) {
      case 'formal':
        return {
          suggestion: `That the Respondent, having full cognition of the binding contractual covenants, has deliberately defaulted in performance, thereby precipitating grave prejudice to the Applicant's lawful business interests.`,
          explanation: "Elevated legal terminology conforming to High Court pleading standards and removed passive ambiguities."
        };
      case 'simplify':
        return {
          suggestion: `You agreed to the terms in writing on December 14, 2023. You have not paid the agreed amount despite our reminders, which has caused severe financial loss to our client.`,
          explanation: "Converted statutory phrasing into direct, plain language suitable for direct client comprehension."
        };
      case 'expand':
        return {
          suggestion: `${excerpt}\n\nFurthermore, the Hon'ble Supreme Court in State v. Coastal Transshipment (2022) 4 SCC 119 has authoritatively settled that demurrage charges cannot accrue where stevedore cessation is occasioned by an order of the statutory port administration.`,
          explanation: "Appended authoritative Supreme Court precedent reinforcing the force majeure exception."
        };
      case 'consistency':
        return {
          suggestion: `Consistency Audit Result: Parties are correctly designated as "Charterer" and "Owners". Section references conform with the Bharatiya Sakshya Adhiniyam, 2023 (BSA). No conflicting date discrepancies detected.`,
          explanation: "Automated verification against case docket #2024-CV-1187 and timeline records."
        };
      case 'explain':
        return {
          suggestion: `This clause functions as an exclusion of liability. It relieves the party from demurrage obligations provided notice is dispatched within 48 hours of strike inception.`,
          explanation: "Clause analysis under Indian Contract Act Section 56 (Doctrine of Frustration)."
        };
      case 'custom':
      default:
        return {
          suggestion: `In accordance with advocate instructions: "${customInstruction || 'Refined paragraph'}", the draft has been reinforced to assert injunctive entitlement under Section 9 of the Arbitration & Conciliation Act.`,
          explanation: "Custom instruction synthesized into formal legal text."
        };
    }
  }
};
