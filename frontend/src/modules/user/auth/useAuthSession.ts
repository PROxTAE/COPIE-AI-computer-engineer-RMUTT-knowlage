"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { configureApiAuth } from "@/modules/core";

import { useUserStore } from "../userStore";
import { clearToken, getToken } from "./token";

export function useAuthSession() {
  const router = useRouter();
  const status = useUserStore((state) => state.status);
  const loadMe = useUserStore((state) => state.loadMe);

  useEffect(() => {
    configureApiAuth({
      getToken,
      clearToken,
      onUnauthorized: () => {
        useUserStore.getState().clearSession();
        router.replace("/login");
      },
    });
    if (useUserStore.getState().status === "idle") void loadMe();
  }, [loadMe, router]);

  return status;
}
