import { INITIAL_EVENTS } from '../mock/mockCalendar';

let eventsStore = [...INITIAL_EVENTS];

export const calendarService = {
  getAllEvents: async () => {
    return [...eventsStore];
  },

  getEventsByDate: async (dateString) => {
    return eventsStore.filter(e => e.date === dateString);
  },

  addEvent: async (eventData) => {
    const newEvent = {
      id: `evt-${Date.now()}`,
      date: eventData.date,
      time: eventData.time || "10:00 AM",
      title: eventData.title,
      caseNumber: eventData.caseNumber || null,
      eventType: eventData.eventType || "hearing",
      court: eventData.court || null,
      location: eventData.location || "Chambers",
      description: eventData.description || "",
      priority: eventData.priority || "normal"
    };
    eventsStore = [...eventsStore, newEvent];
    return newEvent;
  }
};
