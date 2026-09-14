/**
 * caseService.js
 * 
 * Case management service connected to LegalAI FastAPI backend (/api/v1/cases).
 * Automatically preserves compatibility with existing frontend schema.
 */

import { apiClient } from './apiClient';
import { INITIAL_CASES } from '../mock/mockCases';

let fallbackCases = [...INITIAL_CASES];

export const caseService = {
  getAllCases: async () => {
    try {
      const data = await apiClient.get('/api/v1/cases');
      if (Array.isArray(data) && data.length > 0) {
        fallbackCases = data;
        return data;
      }
      return fallbackCases;
    } catch (err) {
      console.warn('Backend /api/v1/cases unavailable, using cached matters:', err.message);
      return fallbackCases;
    }
  },

  getCaseById: async (id) => {
    try {
      return await apiClient.get(`/api/v1/cases/${id}`);
    } catch (err) {
      console.warn(`Backend /api/v1/cases/${id} unavailable, using cached matter:`, err.message);
      return fallbackCases.find(c => c.id === id || c.caseNumber === id) || null;
    }
  },

  addCase: async (newCaseData) => {
    try {
      const created = await apiClient.post('/api/v1/cases', {
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
      });
      fallbackCases = [created, ...fallbackCases];
      return created;
    } catch (err) {
      console.warn('Backend addCase failed, using local store:', err.message);
      const localCase = {
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
      fallbackCases = [localCase, ...fallbackCases];
      return localCase;
    }
  },

  updateCaseStatus: async (id, status) => {
    try {
      const updated = await apiClient.patch(`/api/v1/cases/${id}/status`, { status });
      fallbackCases = fallbackCases.map(c => c.id === id ? updated : c);
      return updated;
    } catch (err) {
      console.warn('Backend updateCaseStatus failed, updating local store:', err.message);
      fallbackCases = fallbackCases.map(c => c.id === id ? { ...c, status } : c);
      return fallbackCases.find(c => c.id === id);
    }
  }
};
