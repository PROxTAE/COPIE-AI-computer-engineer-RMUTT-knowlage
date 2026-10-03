"use client";

import { notifyApiAuthChanged } from "@/modules/core";

const TOKEN_KEY = "copie_access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(TOKEN_KEY, token);
  notifyApiAuthChanged();
}

export function clearToken(): void {
  if (typeof window !== "undefined") {
    try {
      window.localStorage.removeItem(TOKEN_KEY);
    } catch {
      // The in-memory session is still cleared when storage is unavailable.
    }
  }
  notifyApiAuthChanged();
}
