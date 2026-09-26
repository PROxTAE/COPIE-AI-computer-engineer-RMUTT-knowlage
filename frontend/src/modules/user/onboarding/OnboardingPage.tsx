"use client";

import { AppHeader } from "@/modules/core";
import { CopieMascot } from "@/modules/mascot";

import { AuthGuard } from "../auth/AuthGuard";
import { useUserStore } from "../userStore";
import { OnboardingForm } from "./OnboardingForm";

function OnboardingContent() {
  const user = useUserStore((state) => state.user);
  if (!user) return null;

  return (
    <main className="copie-ui flex min-h-dvh flex-col overflow-y-auto">
      <div className="copie-floor" aria-hidden="true" />
      <AppHeader status="ONBOARDING // 01" />
      <section className="relative z-10 mx-auto grid w-full max-w-[1500px] flex-1 items-center gap-8 px-5 pb-10 sm:px-10 lg:grid-cols-[minmax(0,1.1fr)_minmax(380px,0.9fr)]">
        <div className="mx-auto flex w-full max-w-3xl flex-col gap-5 lg:mx-0">
          <span className="copie-eyebrow">NEW USER ONBOARDING</span>
          <div>
            <h1 className="copie-heading text-5xl sm:text-6xl">ทำความรู้จักคุณ</h1>
            <p className="mt-2 text-xl font-semibold text-cyber-muted sm:text-2xl">
              เพื่อให้ COPIE ตอบได้ตรงกับคุณ
            </p>
          </div>
          <div className="copie-panel p-5 sm:p-7">
            <OnboardingForm user={user} />
          </div>
        </div>
        <div className="relative hidden min-h-[520px] place-items-center lg:grid">
          <div className="copie-halo absolute" aria-hidden="true" />
          <CopieMascot state="welcome" priority className="relative max-h-[64dvh] w-auto!" />
        </div>
      </section>
    </main>
  );
}

export function OnboardingPage() {
  return (
    <AuthGuard>
      <OnboardingContent />
    </AuthGuard>
  );
}
