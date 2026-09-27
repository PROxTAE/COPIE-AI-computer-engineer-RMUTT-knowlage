"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Headphones } from "lucide-react";

import { CyberHudFrame } from "@/modules/core";
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
  const [showDevLogin, setShowDevLogin] = useState(false);

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
    <main className="copie-ui relative flex min-h-dvh flex-col overflow-hidden bg-gradient-to-b from-[#f8fbff] to-[#edf5ff]">
      {/* Outer Cyber HUD Frame with Brackets & Rails */}
      <CyberHudFrame showStatusFooter={false} />

      <div className="copie-floor" aria-hidden="true" />

      {/* Top Header Bar */}
      <header className="relative z-30 flex items-center justify-between px-6 py-6 sm:px-12">
        <div className="flex items-center gap-4">
          <span className="copie-wordmark text-3xl sm:text-4xl font-black text-[#080b12] tracking-tighter">
            COPIE
          </span>
          <span className="border-l-2 border-[#155ff2] pl-4 font-label text-[10px] sm:text-[11px] font-bold uppercase leading-tight tracking-[0.16em] text-[#6b82a6]">
            AI ASSISTANT<br />FOR YOUR IDEAS
          </span>
        </div>
        <div className="hidden sm:flex items-center gap-3 font-label text-[11px] font-bold tracking-[0.2em] text-[#6b82a6] uppercase">
          <span>BUILD A BRIGHTER TOMORROW</span>
          <span className="h-0.5 w-6 bg-[#155ff2]" />
        </div>
      </header>

      {/* Main Content Area */}
      <section className="relative z-20 mx-auto grid w-full max-w-[1600px] flex-1 items-center gap-6 sm:gap-8 px-4 sm:px-12 pb-8 lg:grid-cols-[minmax(0,1.1fr)_minmax(420px,0.9fr)]">
        {/* Left Column: Welcome & Google Login */}
        <div className="flex flex-col gap-5 sm:gap-6 max-w-xl">
          {/* Mobile Mascot Preview */}
          <div className="flex justify-center lg:hidden py-1">
            <CopieMascot
              state="welcome"
              priority
              className="max-h-[140px] sm:max-h-[180px] w-auto drop-shadow-[0_10px_20px_rgba(21,95,242,0.14)]"
            />
          </div>

          {/* Eyebrow */}
          <div className="flex items-center gap-2">
            <span className="size-2 bg-[#155ff2]" />
            <span className="font-label text-xs font-bold tracking-[0.2em] text-[#155ff2] uppercase">
              AI AGENT FOR EDUCATION
            </span>
          </div>

          {/* Heading */}
          <div>
            <div className="flex items-center">
              <span className="inline-block w-2 h-10 sm:h-14 bg-[#00d4ff] rounded-full mr-3 sm:mr-4 shrink-0" />
              <h1 className="copie-heading font-display text-3xl sm:text-5xl lg:text-6xl font-black italic tracking-tight text-[#080b12]">
                ยินดีต้อนรับสู่ <span className="not-italic font-black text-black">COPIE</span>
              </h1>
            </div>
            <p className="mt-2 sm:mt-3 pl-2 sm:pl-6 font-display text-lg sm:text-2xl font-bold text-[#080b12]/80">
              ผู้ช่วย AI ภาควิชาวิศวกรรมคอมพิวเตอร์
            </p>
          </div>

          {/* Login Actions */}
          <div className="pl-0 sm:pl-6 pt-1 sm:pt-2 flex flex-col gap-3">
            {checkingSession ? (
              <p className="font-medium text-cyber-muted" role="status">
                กำลังตรวจสอบการเข้าสู่ระบบ...
              </p>
            ) : (
              <>
                <GoogleSignInButton
                  onAuthenticated={routeUser}
                  onOpenDevLogin={() => setShowDevLogin(true)}
                />
                <p className="text-sm font-medium text-[#6b82a6]">
                  ใช้บัญชี Google เพื่อเริ่มต้นใช้งาน COPIE
                </p>

                {/* Dev Login for local development */}
                <div className="pt-2">
                  <button
                    type="button"
                    onClick={() => setShowDevLogin((prev) => !prev)}
                    className="text-xs text-[#6b82a6] hover:text-[#155ff2] underline font-medium cursor-pointer"
                  >
                    {showDevLogin ? "ซ่อนโหมด Dev Login" : "หรือเข้าสู่ระบบด้วย Dev Account"}
                  </button>
                  {showDevLogin && (
                    <div className="mt-3">
                      <DevLoginForm onAuthenticated={routeUser} />
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {/* Bottom Left Support */}
          <div className="pl-0 sm:pl-6 pt-4 sm:pt-8 mt-auto flex items-center gap-3 text-xs text-[#080b12]">
            <div className="flex size-9 items-center justify-center rounded-full bg-blue-50 text-[#155ff2] shrink-0">
              <Headphones className="size-5" />
            </div>
            <div>
              <p className="font-bold text-[#080b12]">หากต้องการความช่วยเหลือ</p>
              <p className="text-[#6b82a6]">ติดต่อผู้ดูแลระบบ</p>
            </div>
          </div>
        </div>

        {/* Right Column: Mascot, Halo, and Cyber Tag */}
        <div className="relative hidden min-h-[540px] items-center justify-center lg:flex">
          {/* Circular Hologram Halo */}
          <div className="copie-halo absolute max-w-[620px] aspect-square pointer-events-none" aria-hidden="true" />

          {/* Mascot */}
          <div className="relative z-10">
            <CopieMascot
              state="welcome"
              priority
              className="relative max-h-[min(65dvh,580px)] w-auto! drop-shadow-[0_20px_40px_rgba(21,95,242,0.18)]"
            />
          </div>

          {/* Vertical Tech Badges on the right */}
          <div className="absolute right-0 top-1/4 flex flex-col gap-8 text-right font-label text-[10px] font-bold tracking-[0.2em] text-[#6b82a6] select-none">
            <div className="flex items-start gap-2">
              <span className="size-2 rounded-full bg-[#155ff2] mt-1 shrink-0" />
              <div className="text-left leading-relaxed">
                <p>ASK</p>
                <p>EXPLORE</p>
                <p>LEARN</p>
                <p>GROW</p>
                <p>TOGETHER</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <span className="size-2 rounded-full bg-[#155ff2] shrink-0" />
              <div className="text-left font-bold text-[#080b12]">
                <p>COPIE</p>
                <p className="text-[9px] text-[#6b82a6]">AI AGENT ONLINE</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Bottom Footer Tagline */}
      <footer className="relative z-30 flex items-center justify-between px-6 py-4 sm:px-12 text-[#6b82a6] font-label text-[11px] font-bold tracking-[0.16em]">
        <div className="flex items-center gap-2">
          <span className="h-0.5 w-6 bg-[#155ff2]" />
          <span>YOUR IDEAS, BRIGHTER TOGETHER</span>
        </div>
      </footer>
    </main>
  );
}
