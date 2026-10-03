"use client";

import type { ReactNode } from "react";
import { useEffect } from "react";
import { Button } from "@heroui/react";
import { usePathname, useRouter } from "next/navigation";

import { useUserStore } from "../userStore";
import { useAuthSession } from "./useAuthSession";

type AuthGuardProps = { children: ReactNode };

function SessionStatus({ message }: { message: string }) {
  return (
    <main className="copie-ui grid min-h-dvh place-items-center px-5">
      <div className="copie-panel relative z-10 max-w-md p-7 text-center">
        <span className="copie-eyebrow">USER SESSION</span>
        <p className="mt-4 text-cyber-muted" role="status">{message}</p>
      </div>
    </main>
  );
}

export function AuthGuard({ children }: AuthGuardProps) {
  const pathname = usePathname();
  const router = useRouter();
  const status = useAuthSession();
  const user = useUserStore((state) => state.user);
  const sessionError = useUserStore((state) => state.sessionError);
  const loadMe = useUserStore((state) => state.loadMe);

  let redirectTo: string | null = null;
  if (status === "anonymous") redirectTo = "/login";
  if (status === "authenticated" && user && !user.onboarded && pathname !== "/onboarding") {
    redirectTo = "/onboarding";
  }
  if (status === "authenticated" && user?.onboarded && pathname === "/onboarding") {
    redirectTo = "/chat";
  }

  useEffect(() => {
    if (redirectTo) router.replace(redirectTo);
  }, [redirectTo, router]);

  if (status === "error") {
    return (
      <main className="copie-ui grid min-h-dvh place-items-center px-5">
        <div className="copie-panel relative z-10 max-w-md p-7 text-center" role="alert">
          <span className="copie-eyebrow">CONNECTION ERROR</span>
          <p className="mt-4 text-cyber-muted">{sessionError}</p>
          <Button className="mt-5" variant="primary" onPress={() => { void loadMe(); }}>
            ลองอีกครั้ง
          </Button>
        </div>
      </main>
    );
  }

  if (status !== "authenticated" || !user || redirectTo) {
    return <SessionStatus message="กำลังตรวจสอบการเข้าสู่ระบบ..." />;
  }

  return children;
}
