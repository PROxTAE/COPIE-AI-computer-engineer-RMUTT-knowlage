"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

import { AppHeader } from "@/modules/core";
import { CopieMascot } from "@/modules/mascot";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";
import { DevLoginForm } from "./DevLoginForm";
import { GoogleSignInButton } from "./GoogleSignInButton";
import { useAuthSession } from "./useAuthSession";

export function LoginPage() {
  const router = useRouter();
  const status = useAuthSession();
  const user = useUserStore((state) => state.user);

  const routeUser = (authenticatedUser: User) => {
    router.replace(authenticatedUser.onboarded ? "/chat" : "/onboarding");
  };

  useEffect(() => {
    if (status === "authenticated" && user) {
      router.replace(user.onboarded ? "/chat" : "/onboarding");
    }
  }, [router, status, user]);

  const checkingSession = status === "idle" || status === "loading" || status === "authenticated";

  return (
    <main className="copie-ui flex min-h-dvh flex-col overflow-y-auto">
      <div className="copie-floor" aria-hidden="true" />
      <AppHeader status="AUTH // READY" />
      <section className="relative z-10 mx-auto grid w-full max-w-[1500px] flex-1 items-center gap-8 px-5 pb-10 sm:px-10 lg:grid-cols-[minmax(0,0.9fr)_minmax(420px,1.1fr)]">
        <div className="mx-auto flex w-full max-w-xl flex-col gap-5 lg:mx-0">
          <span className="copie-eyebrow">AI AGENT FOR EDUCATION</span>
          <div>
            <h1 className="copie-heading text-5xl sm:text-6xl">ยินดีต้อนรับสู่ COPIE</h1>
            <p className="mt-3 text-xl font-semibold text-cyber-muted sm:text-2xl">
              ผู้ช่วย AI ภาควิชาวิศวกรรมคอมพิวเตอร์
            </p>
          </div>
          <div className="copie-panel flex flex-col gap-5 p-5 sm:p-7">
            {checkingSession ? (
              <p className="text-center text-cyber-muted" role="status">กำลังตรวจสอบการเข้าสู่ระบบ...</p>
            ) : (
              <>
                <GoogleSignInButton onAuthenticated={routeUser} />
                <p className="text-center text-sm text-cyber-muted">ใช้บัญชี Google เพื่อเริ่มต้นใช้งาน COPIE</p>
                {process.env.NODE_ENV === "development" && (
                  <DevLoginForm onAuthenticated={routeUser} />
                )}
              </>
            )}
          </div>
          <p className="text-sm text-cyber-muted">
            หากต้องการความช่วยเหลือ กรุณาติดต่อผู้ดูแลระบบของภาควิชา
          </p>
        </div>
        <div className="relative hidden min-h-[520px] place-items-center lg:grid">
          <div className="copie-halo absolute" aria-hidden="true" />
          <CopieMascot state="welcome" priority className="relative max-h-[66dvh] w-auto!" />
        </div>
      </section>
    </main>
  );
}
