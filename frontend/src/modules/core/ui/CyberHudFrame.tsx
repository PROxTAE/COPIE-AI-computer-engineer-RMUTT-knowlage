import type { ReactNode } from "react";

interface CyberHudFrameProps {
  children?: ReactNode;
  showStatusFooter?: boolean;
}

export function CyberHudFrame({ children, showStatusFooter = true }: CyberHudFrameProps) {
  return (
    <div className="pointer-events-none fixed inset-0 z-20 overflow-hidden" aria-hidden="true">
      {/* Corner brackets live in the outer 12px margin (arms 24px), clear of header and footer text
          that starts at 48px from the edge. */}
      <div className="copie-hud-corner left-3 top-3 rounded-tl-lg border-l-2 border-t-2">
        <span className="copie-hud-dot -left-[3px] -top-[3px]" />
      </div>
      <div className="copie-hud-corner right-3 top-3 rounded-tr-lg border-r-2 border-t-2">
        <span className="copie-hud-dot -right-[3px] -top-[3px]" />
      </div>
      <div className="copie-hud-corner bottom-3 left-3 rounded-bl-lg border-b-2 border-l-2">
        <span className="copie-hud-dot -bottom-[3px] -left-[3px]" />
      </div>
      <div className="copie-hud-corner bottom-3 right-3 rounded-br-lg border-b-2 border-r-2">
        <span className="copie-hud-dot -bottom-[3px] -right-[3px]" />
      </div>

      {/* Left side notch & ticks */}
      <div className="absolute left-3 top-1/2 -translate-y-1/2 hidden lg:flex flex-col gap-3">
        <div className="h-4 w-1 bg-cyber-blue/70 rounded-full" />
        <div className="h-1.5 w-1.5 bg-cyber-glow" />
        <div className="h-1.5 w-1.5 bg-cyber-blue/40" />
      </div>

      {/* Right side dotted rail (from mockups) */}
      <div className="absolute right-3 top-1/2 -translate-y-1/2 hidden lg:flex flex-col items-center gap-2">
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
