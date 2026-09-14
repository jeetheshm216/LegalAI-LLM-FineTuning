/**
 * authService.js
 * 
 * Authentication service for LegalAI Frontend.
 * 
 * NOTE: Backend authentication does not yet exist in the LegalAI backend.
 * This service implements the standard client-side authentication contract,
 * preserving demo session state across page refreshes via localStorage.
 * When backend auth endpoints (e.g. /api/v1/auth/login) are implemented,
 * they can be hooked directly into apiClient.
 */

import { INITIAL_USER } from '../mock/mockUser';

const AUTH_STORAGE_KEY = 'legalai_auth_user';
const TOKEN_STORAGE_KEY = 'legalai_auth_token';

function getStoredUser() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    return raw ? JSON.parse(raw) : { ...INITIAL_USER };
  } catch {
    return { ...INITIAL_USER };
  }
}

let currentUser = getStoredUser();
let isAuthenticated = true; // Default session active for lawyer chambers workflow

export const authService = {
  getCurrentUser: () => currentUser,
  isAuthenticated: () => isAuthenticated,

  login: async ({ email, password, rememberMe }) => {
    await new Promise(r => setTimeout(r, 400));
    if (email === "error@vance-legal.org") {
      throw new Error("That email and password combination doesn't match our records.");
    }
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
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(currentUser));
      localStorage.setItem(TOKEN_STORAGE_KEY, "legalai-demo-bearer-token");
    } catch {
      // Storage unavailable
    }
    return { success: true, user: currentUser };
  },

  logout: async () => {
    isAuthenticated = false;
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
    } catch {
      // Ignore
    }
    return { success: true };
  },

  updateSettings: (newSettings) => {
    currentUser = { ...currentUser, ...newSettings };
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(currentUser));
    } catch {
      // Ignore
    }
    return currentUser;
  }
};
