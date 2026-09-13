import { INITIAL_TIMELINE } from '../mock/mockTimeline';

let timelineStore = [...INITIAL_TIMELINE];

export const timelineService = {
  getTimelineByCase: async (caseId) => {
    return timelineStore.filter(t => t.caseId === caseId);
  },

  getAllTimelineEvents: async () => {
    return [...timelineStore];
  },

  addTimelineEvent: async (eventData) => {
    const newEvent = {
      id: `time-${Date.now()}`,
      caseId: eventData.caseId,
      timestamp: new Date().toISOString().replace('T', ' ').substring(0, 16),
      relativeTime: "Just now",
      eventType: eventData.eventType || "note",
      title: eventData.title,
      author: eventData.author || "Adv. Elena Vance",
      isAI: eventData.isAI || false,
      summary: eventData.summary,
      details: eventData.details || eventData.summary,
      relatedDocument: eventData.relatedDocument || null
    };
    timelineStore = [newEvent, ...timelineStore];
    return newEvent;
  }
};
