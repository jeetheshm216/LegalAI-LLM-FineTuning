import { INITIAL_USER } from '../mock/mockUser';

let currentUser = { ...INITIAL_USER };
let isAuthenticated = true; // start authenticated by default for seamless preview, but allow full logout/login toggle

export const authService = {
  getCurrentUser: () => currentUser,
  isAuthenticated: () => isAuthenticated,

  login: async ({ email, password, rememberMe }) => {
    await new Promise(r => setTimeout(r, 400));
    if (email === "error@vance-legal.org") {
      throw new Error("That email and password combination doesn't match our records.");
    }
    // Return requires2FA flag
    return {
      success: true,
      requires2FA: true,
      tempToken: "temp-session-token-legal-ai"
    };
  },

  verify2FA: async ({ code }) => {
    await new Promise(r => setTimeout(r, 400));
    if (code !== "123456" && code !== "888888") {
      throw new Error("Invalid verification code. Please check your authenticator app.");
    }
    isAuthenticated = true;
    return { success: true, user: currentUser };
  },

  logout: async () => {
    isAuthenticated = false;
    return { success: true };
  },

  updateSettings: (newSettings) => {
    currentUser = { ...currentUser, ...newSettings };
    return currentUser;
  }
};
