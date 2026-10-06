"use client";

import { CyberHudFrame } from "@/modules/core";
import { CopieMascot } from "@/modules/mascot";

import { AuthGuard } from "../auth/AuthGuard";
import { useUserStore } from "../userStore";
import { OnboardingForm } from "./OnboardingForm";

function OnboardingContent() {
  const user = useUserStore((state) => state.user);
  if (!user) return null;

  return (
    <main className="copie-ui relative flex min-h-dvh flex-col overflow-y-auto overflow-x-hidden bg-gradient-to-b from-[#f8fbff] to-[#edf5ff]">
      {/* Outer Cyber HUD Frame */}
      <CyberHudFrame showStatusFooter={false} />

      <div className="copie-floor" aria-hidden="true" />

      {/* Top Header Bar */}
      <header className="relative z-30 flex items-center justify-between px-4 py-4 sm:px-12 sm:py-6">
        <div className="flex items-center gap-3 sm:gap-4">
          <span className="copie-wordmark text-2xl sm:text-4xl font-black text-cyber-strong tracking-tighter">
            COPIE
          </span>
          <span className="hidden sm:block border-l-2 border-cyber-blue pl-4 font-label text-[10px] sm:text-[11px] font-bold uppercase leading-tight tracking-[0.16em] text-cyber-subtle">
            AI ASSISTANT<br />FOR YOUR IDEAS
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-3 font-label text-[11px] font-bold tracking-[0.2em] text-cyber-subtle uppercase">
          <span>BUILD A BRIGHTER TOMORROW</span>
          <span className="h-0.5 w-6 bg-cyber-blue" />
        </div>
      </header>

      {/* Main Content Area */}
      <section className="relative z-20 mx-auto grid w-full max-w-[1600px] flex-1 items-center gap-6 sm:gap-8 px-4 sm:px-12 pb-8 lg:grid-cols-[minmax(0,1.15fr)_minmax(420px,0.85fr)]">
        {/* Left Column: Form & Step Progress */}
        <div className="flex flex-col gap-5 sm:gap-6 max-w-2xl">
          {/* Eyebrow & Step Progress Row */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="size-2 bg-cyber-blue" />
              <span className="font-label text-xs font-bold tracking-[0.2em] text-cyber-blue uppercase">
                NEW USER ONBOARDING
              </span>
            </div>

            {/* Step 01 / 01 indicator from mockup 02-onboarding */}
            <div className="flex flex-col items-end gap-1.5">
              <div className="font-label text-xs font-bold text-cyber-strong">
                ขั้นตอน <span className="italic text-cyber-blue text-sm">01</span> / <span className="italic text-cyber-blue text-sm">01</span>
              </div>
              <div className="flex items-center gap-1 w-24">
                <span className="h-1.5 w-1.5 rounded-full bg-cyber-blue" />
                <span className="h-1 flex-1 rounded-full bg-cyber-blue" />
                <span className="h-1.5 w-1.5 rounded-full bg-cyber-edge" />
              </div>
            </div>
          </div>

          {/* Heading */}
          <div>
            <div className="flex items-center">
              <span className="inline-block w-2 h-10 sm:h-14 bg-cyber-glow rounded-full mr-3 sm:mr-4 shrink-0" />
              <h1 className="copie-heading font-display text-3xl sm:text-5xl lg:text-6xl font-black italic tracking-tight text-cyber-strong">
                ทำความรู้จักคุณ
              </h1>
            </div>
            <p className="mt-2 pl-0 sm:pl-6 font-display text-lg sm:text-2xl font-bold text-cyber-strong/80">
              เพื่อให้ COPIE ตอบได้ตรงกับคุณ
            </p>
          </div>

          {/* Form */}
          <div className="pl-0 sm:pl-6 pt-1 sm:pt-2">
            <OnboardingForm user={user} />
          </div>
        </div>

        {/* Right Column: Mascot, Halo, and Cyber Tag */}
        <div className="relative hidden min-h-[540px] items-center justify-center lg:flex">
          <div className="copie-halo absolute max-w-[620px] aspect-square pointer-events-none" aria-hidden="true" />
          <div className="relative z-10">
            <CopieMascot
              state="welcome"
              priority
              className="relative max-h-[min(65dvh,580px)] w-auto! drop-shadow-[0_20px_40px_rgb(var(--copie-accent-rgb)/0.18)]"
            />
          </div>

          {/* Tech Badges on the right */}
          <div className="absolute right-0 top-1/4 flex flex-col gap-8 text-right font-label text-[10px] font-bold tracking-[0.2em] text-cyber-subtle select-none">
            <div className="flex items-start gap-2">
              <span className="size-2 rounded-full bg-cyber-blue mt-1 shrink-0" />
              <div className="text-left leading-relaxed">
                <p>ASK</p>
                <p>EXPLORE</p>
                <p>LEARN</p>
                <p>GROW</p>
                <p>TOGETHER</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-cyber-blue shrink-0" />
              <div className="text-left font-bold text-cyber-strong">
                <p>COPIE</p>
                <p className="text-[9px] text-cyber-subtle">AI AGENT ONLINE</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom Footer Tagline */}
      <footer className="relative z-30 flex items-center justify-between px-6 py-4 sm:px-12 text-cyber-subtle font-label text-[11px] font-bold tracking-[0.16em]">
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-6 bg-cyber-blue" />
          <span>YOUR IDEAS, BRIGHTER TOGETHER</span>
        </div>
      </footer>
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
