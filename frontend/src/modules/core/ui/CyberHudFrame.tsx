import type { ReactNode } from "react";

interface CyberHudFrameProps {
  children?: ReactNode;
  showStatusFooter?: boolean;
}

export function CyberHudFrame({ children, showStatusFooter = true }: CyberHudFrameProps) {
  return (
    <div className="pointer-events-none fixed inset-0 z-20 overflow-hidden" aria-hidden="true">
      {/* Top-Left Corner Bracket */}
      <div className="absolute top-4 left-4 sm:top-6 sm:left-8 hidden md:block">
        <div className="h-2 w-2 bg-cyber-glow shadow-[0_0_8px_var(--copie-glow)]" />
        <div className="mt-1 h-8 w-8 sm:h-12 sm:w-12 rounded-tl-xl border-t-2 border-l-2 border-cyber-blue" />
      </div>

      {/* Top-Right Corner Bracket */}
      <div className="absolute top-4 right-4 sm:top-6 sm:right-8 hidden md:flex flex-col items-end">
        <div className="h-2 w-2 bg-cyber-glow shadow-[0_0_8px_var(--copie-glow)]" />
        <div className="mt-1 h-8 w-8 sm:h-12 sm:w-12 rounded-tr-xl border-t-2 border-r-2 border-cyber-blue" />
      </div>

      {/* Bottom-Left Corner Bracket */}
      <div className="absolute bottom-4 left-4 sm:bottom-6 sm:left-8 hidden md:flex flex-col justify-end">
        <div className="mb-1 h-8 w-8 sm:h-12 sm:w-12 rounded-bl-xl border-b-2 border-l-2 border-cyber-blue" />
        <div className="h-2 w-2 bg-cyber-glow shadow-[0_0_8px_var(--copie-glow)]" />
      </div>

      {/* Bottom-Right Corner Bracket */}
      <div className="absolute bottom-4 right-4 sm:bottom-6 sm:right-8 hidden md:flex flex-col items-end justify-end">
        <div className="mb-1 h-8 w-8 sm:h-12 sm:w-12 rounded-br-xl border-b-2 border-r-2 border-cyber-blue" />
        <div className="h-2 w-2 bg-cyber-glow shadow-[0_0_8px_var(--copie-glow)]" />
      </div>

      {/* Left side notch & ticks */}
      <div className="absolute left-4 sm:left-8 top-1/2 -translate-y-1/2 hidden lg:flex flex-col gap-3">
        <div className="h-4 w-1 bg-cyber-blue/70 rounded-full" />
        <div className="h-1.5 w-1.5 bg-cyber-glow" />
        <div className="h-1.5 w-1.5 bg-cyber-blue/40" />
      </div>

      {/* Right side dotted rail (from mockups) */}
      <div className="absolute right-4 sm:right-8 top-1/2 -translate-y-1/2 hidden lg:flex flex-col items-center gap-2">
        <div className="h-1.5 w-1.5 rounded-full bg-cyber-blue" />
        <div className="h-1.5 w-1.5 rounded-full bg-cyber-glow" />
        <div className="h-1.5 w-1.5 rounded-full bg-cyber-blue/70" />
        <div className="h-1.5 w-1.5 rounded-full bg-cyber-glow/80" />
        <div className="h-1.5 w-1.5 rounded-full bg-cyber-blue/40" />
        <div className="h-1.5 w-1.5 rounded-full bg-cyber-glow/40" />
      </div>

      {/* Floating cyber chips / particles around */}
      <div className="absolute top-[28%] left-[22%] h-2 w-2 bg-cyber-glow/30 pointer-events-none hidden lg:block" />
      <div className="absolute top-[18%] right-[25%] h-2.5 w-2.5 bg-cyber-glow/35 pointer-events-none hidden lg:block" />
      <div className="absolute bottom-[24%] left-[16%] h-2 w-2 bg-cyber-blue/25 pointer-events-none hidden lg:block" />
      <div className="absolute bottom-[22%] right-[18%] h-2 w-2 bg-cyber-glow/30 pointer-events-none hidden lg:block" />

      {/* Bottom-right tech label */}
      {showStatusFooter && (
        <div className="absolute bottom-5 right-14 sm:right-20 hidden md:flex items-center gap-2 font-label text-[10px] font-bold tracking-[0.18em] text-cyber-subtle uppercase select-none">
          <span className="h-1 w-6 rounded-full bg-gradient-to-r from-cyber-blue to-cyber-glow" />
          <span>ONLINE // READY FOR YOUR IDEAS</span>
        </div>
      )}

      {children}
    </div>
  );
}
