import { INITIAL_CASES } from '../mock/mockCases';

let casesStore = [...INITIAL_CASES];

export const caseService = {
  getAllCases: async () => {
    return [...casesStore];
  },

  getCaseById: async (id) => {
    return casesStore.find(c => c.id === id || c.caseNumber === id) || null;
  },

  addCase: async (newCaseData) => {
    const newCase = {
      id: `case-${Date.now()}`,
      caseNumber: newCaseData.caseNumber || `2026-CV-${Math.floor(1000 + Math.random() * 9000)}`,
      title: newCaseData.title,
      client: newCaseData.client,
      opposingParty: newCaseData.opposingParty || "Undisclosed",
      court: newCaseData.court,
      caseType: newCaseData.caseType,
      status: newCaseData.status || "Active",
      priority: newCaseData.priority || "normal",
      filedDate: newCaseData.filedDate || new Date().toISOString().split('T')[0],
      nextHearing: newCaseData.nextHearing || "None scheduled",
      hearingCountdownDays: newCaseData.hearingCountdownDays || null,
      assignedLawyer: newCaseData.assignedLawyer || "Adv. Elena Vance",
      description: newCaseData.description || "",
      matterSummary: newCaseData.matterSummary || newCaseData.description || "",
      tags: newCaseData.tags || ["New Matter"]
    };
    casesStore = [newCase, ...casesStore];
    return newCase;
  },

  updateCaseStatus: async (id, status) => {
    casesStore = casesStore.map(c => c.id === id ? { ...c, status } : c);
    return casesStore.find(c => c.id === id);
  }
};
