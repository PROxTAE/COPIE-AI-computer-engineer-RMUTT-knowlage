import { CopieMascot } from "@/modules/mascot";

// The interactive workspace is assembled in the following core slices.
export default function Page() {
  return (
    <main className="copie-ui flex min-h-dvh flex-col px-5 py-6 sm:px-10">
      <div className="copie-floor" aria-hidden="true" />
      <header className="relative z-10 flex items-center justify-between gap-4">
        <span className="copie-wordmark">COPIE</span>
        <span className="copie-status flex items-center gap-2">
          <span className="copie-status-dot" /> AI // Active
        </span>
      </header>
      <div className="relative z-10 flex flex-1 flex-col items-center justify-center text-center">
        <div className="copie-halo absolute" aria-hidden="true" />
        <CopieMascot state="idle" priority className="relative max-h-[min(64dvh,680px)] w-auto!" />
        <h1 className="copie-heading mt-2 text-3xl sm:text-4xl">คุยกับ COPIE</h1>
        <p className="mt-2 max-w-lg text-cyber-muted">ผู้ช่วย AI ของภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT</p>
        <p className="copie-status mt-4">พื้นที่สนทนากำลังเตรียมพร้อม</p>
      </div>
    </main>
  );
}
