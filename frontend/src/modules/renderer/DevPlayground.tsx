"use client";

// หน้า /dev — สนามทดสอบของ P6 และเป็นที่ให้ทีมอื่นดู shape ของ AgentResponse ได้โดยไม่ต้องรัน backend
// ไม่เรียก API ใด ๆ ทั้งสิ้น: ทุกอย่างมาจาก MOCKS
import { useState } from "react";
import { MOCKS, MOCK_LABELS, type MockKey } from "./mock";
import { ResponseRenderer, type AssessmentAnswer } from "./ResponseRenderer";
import { FOCUS_RING } from "./components/styles";

type Viewport = "desktop" | "mobile";

const VIEWPORT_WIDTH: Record<Viewport, string> = {
  desktop: "100%",
  mobile: "390px", // ขนาดที่แผนกำหนดให้ทดสอบ responsive
};

export function DevPlayground() {
  const [selected, setSelected] = useState<MockKey>("text");
  const [viewport, setViewport] = useState<Viewport>("desktop");
  const [disabled, setDisabled] = useState(false);
  const [showJson, setShowJson] = useState(false);
  const [log, setLog] = useState<string[]>([]);

  const response = MOCKS[selected];

  const pushLog = (line: string) => {
    const time = new Date().toLocaleTimeString("th-TH", { hour12: false });
    setLog((previous) => [`${time} · ${line}`, ...previous].slice(0, 8));
  };

  const handleAsk = (text: string) => pushLog(`onAsk("${text}")`);

  const handleSubmitAssessment = async (answers: AssessmentAnswer[]) => {
    pushLog(`onSubmitAssessment(${answers.length} ข้อ)`);
    // จำลองเวลารอ backend เพื่อดูสถานะ disabled ของฟอร์ม
    await new Promise((resolve) => setTimeout(resolve, 800));
  };

  return (
    <main className="mx-auto flex max-w-6xl flex-col gap-6 px-4 py-10">
      <header className="flex flex-col gap-1">
        <p className="text-sm text-muted">/dev · P6 (renderer)</p>
        <h1 className="font-display text-3xl font-bold text-deep-navy">Renderer playground</h1>
        <p className="text-muted">แสดง mock ของทุก response_type โดยไม่ต้องมี backend</p>
        <p className="text-sm text-muted">
          ทุก fixture อ้างอิงไฟล์ข้อมูลจริงใน data/ แล้ว · ใช้ได้เฉพาะหน้านี้และ tests ห้าม import ใน /chat
        </p>
      </header>

      <div className="flex flex-col gap-6 lg:flex-row">
        <nav className="flex shrink-0 flex-col gap-1 lg:w-64" aria-label="เลือก fixture">
          {MOCK_LABELS.map((item) => {
            const active = item.key === selected;
            return (
              <button
                key={item.key}
                type="button"
                onClick={() => setSelected(item.key)}
                aria-current={active ? "true" : undefined}
                className={`rounded-lg border px-3 py-2 text-left transition ${FOCUS_RING} ${
                  active
                    ? "border-copie-teal bg-copie-teal/10 text-deep-navy"
                    : "border-transparent bg-surface text-ink hover:border-deep-navy/15"
                }`}
              >
                <span className="block font-medium">{item.label}</span>
                <span className="block text-xs text-muted">{item.note}</span>
              </button>
            );
          })}
        </nav>

        <section className="min-w-0 flex-1 flex flex-col gap-4">
          <div className="flex flex-wrap items-center gap-2 text-sm">
            <ToggleButton active={viewport === "desktop"} onClick={() => setViewport("desktop")}>
              Desktop
            </ToggleButton>
            <ToggleButton active={viewport === "mobile"} onClick={() => setViewport("mobile")}>
              Mobile 390px
            </ToggleButton>
            <span className="mx-1 h-5 w-px bg-deep-navy/15" aria-hidden="true" />
            <ToggleButton active={disabled} onClick={() => setDisabled((value) => !value)}>
              disabled
            </ToggleButton>
            <ToggleButton active={showJson} onClick={() => setShowJson((value) => !value)}>
              ดู JSON
            </ToggleButton>
            <span className="ml-auto text-xs text-muted tabular-nums">
              intent: {response.meta.intent} · tool: {response.meta.tool ?? "—"} · {response.meta.latency_ms} ms
            </span>
          </div>

          <div
            className="rounded-xl border border-deep-navy/10 bg-surface p-5"
            style={{ width: VIEWPORT_WIDTH[viewport], maxWidth: "100%" }}
          >
            <ResponseRenderer
              response={response}
              onAsk={handleAsk}
              onSubmitAssessment={handleSubmitAssessment}
              disabled={disabled}
            />
          </div>

          {showJson && (
            <pre className="max-h-96 overflow-auto rounded-xl border border-deep-navy/10 bg-deep-navy p-4 text-xs leading-5 text-mist">
              {JSON.stringify(response, null, 2)}
            </pre>
          )}

          <section aria-label="callback log" className="rounded-xl border border-deep-navy/10 bg-surface p-4">
            <h2 className="font-display text-sm font-semibold text-deep-navy">Callback log</h2>
            {log.length === 0 ? (
              <p className="mt-1 text-sm text-muted">ยังไม่มีการเรียก callback</p>
            ) : (
              <ul className="mt-2 flex flex-col gap-1 text-sm text-ink">
                {log.map((line, index) => (
                  <li key={`${line}-${index}`} className="tabular-nums">
                    {line}
                  </li>
                ))}
              </ul>
            )}
          </section>
        </section>
      </div>
    </main>
  );
}

function ToggleButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={`rounded-lg border px-3 py-1.5 transition ${FOCUS_RING} ${
        active ? "border-copie-teal bg-copie-teal/10 text-deep-navy" : "border-deep-navy/15 text-muted hover:text-ink"
      }`}
    >
      {children}
    </button>
  );
}
