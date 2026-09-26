"use client";

import { create } from "zustand";

import { api, ApiError } from "@/modules/core";
import type { AuthResponse, ProfileUpdate, User } from "@/types/contract";

import { clearToken, getToken, setToken } from "./auth/token";

export type SessionStatus = "idle" | "loading" | "authenticated" | "anonymous" | "error";

type UserState = {
  user: User | null;
  status: SessionStatus;
  sessionError: string | null;
  loadMe: () => Promise<User | null>;
  loginWithGoogle: (idToken: string) => Promise<User>;
  loginWithDev: (email: string, name: string) => Promise<User>;
  updateProfile: (profile: ProfileUpdate) => Promise<User>;
  clearSession: () => void;
};

let activeLoad: Promise<User | null> | null = null;

function authRequest(path: string, body: object): Promise<AuthResponse> {
  return api<AuthResponse>(path, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

async function completeLogin(request: Promise<AuthResponse>): Promise<User> {
  const response = await request;
  setToken(response.access_token);
  useUserStore.setState({
    user: response.user,
    status: "authenticated",
    sessionError: null,
  });
  return response.user;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  status: "idle",
  sessionError: null,
  loadMe: async () => {
    if (!getToken()) {
      set({ user: null, status: "anonymous", sessionError: null });
      return null;
    }
    if (activeLoad) return activeLoad;

    set({ status: "loading", sessionError: null });
    activeLoad = api<User>("/api/users/me")
      .then((user) => {
        set({ user, status: "authenticated", sessionError: null });
        return user;
      })
      .catch((error: unknown) => {
        if (error instanceof ApiError && error.status === 401) {
          clearToken();
          set({ user: null, status: "anonymous", sessionError: null });
          return null;
        }
        const message = error instanceof ApiError
          ? error.message
          : "ตรวจสอบสถานะการเข้าสู่ระบบไม่สำเร็จ กรุณาลองใหม่";
        set({ user: null, status: "error", sessionError: message });
        return null;
      })
      .finally(() => {
        activeLoad = null;
      });
    return activeLoad;
  },
  loginWithGoogle: (idToken) => completeLogin(
    authRequest("/api/auth/google", { id_token: idToken }),
  ),
  loginWithDev: (email, name) => completeLogin(
    authRequest("/api/auth/dev", { email, name }),
  ),
  updateProfile: async (profile) => {
    const user = await api<User>("/api/users/me/profile", {
      method: "PUT",
      body: JSON.stringify(profile),
    });
    set({ user, status: "authenticated", sessionError: null });
    return user;
  },
  clearSession: () => {
    clearToken();
    set({ user: null, status: "anonymous", sessionError: null });
  },
}));
