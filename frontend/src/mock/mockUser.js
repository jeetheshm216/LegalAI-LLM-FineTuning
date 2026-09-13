export const INITIAL_USER = {
  name: "Adv. Elena Vance",
  email: "e.vance@vance-legal.org",
  barNumber: "NY-BAR-481920 / HC-7819",
  chambers: "Vance & Associates Legal Chambers",
  role: "Senior Advocate / Managing Partner",
  avatarInitials: "EV",
  twoFactorEnabled: true,
  theme: "light", // light, dark, system
  accessibility: {
    fontSize: "default", // small, default, large, xlarge
    contrast: "default", // default, high
    reducedMotion: false,
  },
  aiPreferences: {
    responseLength: "Standard", // Concise, Standard, Detailed
    citationDisplay: "Collapsed", // Inline, Collapsed
    defaultContextBehavior: "always_ask" // always_ask, auto_case
  },
  activeSessions: [
    {
      id: "sess-1",
      device: "MacBook Pro 16 (Current)",
      location: "New York, USA",
      ip: "192.168.1.144",
      lastActive: "Active now"
    },
    {
      id: "sess-2",
      device: "iPad Pro Chambers Desk",
      location: "Chambers Library",
      ip: "10.0.4.12",
      lastActive: "4 hours ago"
    }
  ],
  loginHistory: [
    {
      id: "log-1",
      timestamp: "2026-09-13 08:14:22",
      ip: "192.168.1.144",
      device: "Desktop Chrome (Windows 11)",
      status: "success"
    },
    {
      id: "log-2",
      timestamp: "2026-09-12 09:02:11",
      ip: "192.168.1.144",
      device: "Desktop Chrome (Windows 11)",
      status: "success"
    },
    {
      id: "log-3",
      timestamp: "2026-09-10 18:44:05",
      ip: "185.220.101.5",
      device: "Unknown Safari (Tor Exit)",
      status: "failed"
    }
  ]
};
