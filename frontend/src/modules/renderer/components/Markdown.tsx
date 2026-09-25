// Safe markdown — ห้ามใช้ dangerouslySetInnerHTML และไม่เปิด rehype-raw
// (remark-gfm ให้ตาราง / checklist / strikethrough ตามที่แผนกำหนด)
//
// หน้าตาอิงม็อกอัพ 04-chat-answer / 05-reading-mode:
//   h2 = หัวข้อใหญ่ + แถบซ้าย + เส้น streak · ol = ประเด็นย่อย "01 /" สีฟ้า
// ถ้าส่ง onCitationClick มาด้วย ข้อความ "[3]" ในเนื้อหาจะกลายเป็นปุ่มอ้างอิงที่กดได้
import type { ReactNode } from "react";
import { Children, isValidElement } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

interface MarkdownProps {
  children: string;
  className?: string;
  /** กดที่ badge [n] แล้วให้ SourceViewer เปิดแหล่งที่ n (1-based) */
  onCitationClick?: (index: number) => void;
  /** จำนวน source ที่มีจริง — [n] ที่เกินจากนี้ปล่อยเป็นข้อความธรรมดา */
  citationCount?: number;
}

export function Markdown({ children, className, onCitationClick, citationCount = 0 }: MarkdownProps) {
  const decorate = (nodes: ReactNode): ReactNode =>
    onCitationClick ? withCitations(nodes, onCitationClick, citationCount) : nodes;

  return (
    <div className={className}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children: text }) => <Heading level={1}>{text}</Heading>,
          h2: ({ children: text }) => <Heading level={2}>{text}</Heading>,
          h3: ({ children: text }) => (
            <h3 className="copie-heading font-display text-lg font-semibold text-deep-navy">{text}</h3>
          ),
          p: ({ children: text }) => <p className="leading-8 text-ink">{decorate(text)}</p>,
          // ประเด็นย่อยแบบม็อกอัพ: เลขลำดับ "01 /" ตัวใหญ่เอียงสีฟ้าอยู่ริมซ้าย
          // react-markdown v10 ไม่บอกว่า li อยู่ใน ol หรือ ul จึงสั่งสไตล์จาก ol ลงไปที่ลูกแทน
          ol: ({ children: items }) => (
            <ol className="copie-index flex list-none flex-col gap-4 [counter-reset:copie-idx] [&>li]:relative [&>li]:pl-12 [&>li]:[counter-increment:copie-idx] [&>li]:before:absolute [&>li]:before:left-0 [&>li]:before:top-0 [&>li]:before:font-display [&>li]:before:text-xl [&>li]:before:font-bold [&>li]:before:italic [&>li]:before:text-copie-teal [&>li]:before:[content:counter(copie-idx,decimal-leading-zero)_'_/']">
              {items}
            </ol>
          ),
          li: ({ children: text }) => <li className="leading-8 text-ink">{decorate(text)}</li>,
          ul: ({ children: items }) => (
            <ul className="flex list-disc flex-col gap-1 pl-5 marker:text-copie-teal">{items}</ul>
          ),
          strong: ({ children: text }) => <strong className="font-semibold text-deep-navy">{text}</strong>,
          a: ({ children: text, href }) => (
            <a
              href={href}
              className="text-copie-teal underline underline-offset-2"
              target="_blank"
              rel="noopener noreferrer"
            >
              {text}
            </a>
          ),
          table: ({ children: rows }) => (
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm tabular-nums">{rows}</table>
            </div>
          ),
          th: ({ children: text }) => (
            <th className="border-b border-deep-navy/15 px-3 py-2 text-left font-semibold text-deep-navy">{text}</th>
          ),
          td: ({ children: text }) => (
            <td className="border-b border-deep-navy/10 px-3 py-2 align-top">{decorate(text)}</td>
          ),
          code: ({ children: text }) => <code className="rounded bg-mist px-1.5 py-0.5 text-[0.9em]">{text}</code>,
          blockquote: ({ children: text }) => (
            <blockquote className="border-l-2 border-copie-teal/40 pl-4 text-muted">{text}</blockquote>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}

// หัวข้อคำตอบ: แถบฟ้าด้านซ้าย + เส้น streak ทางขวาตามม็อกอัพ
function Heading({ level, children }: { level: 1 | 2; children: ReactNode }) {
  const Tag = level === 1 ? "h1" : "h2";
  const size = level === 1 ? "text-3xl" : "text-2xl";
  return (
    <div className="flex items-center gap-3">
      <span aria-hidden="true" className="h-8 w-1 shrink-0 rounded-full bg-copie-teal" />
      <Tag className={`copie-heading font-display ${size} font-bold text-deep-navy`}>{children}</Tag>
      <span
        aria-hidden="true"
        className="copie-streak h-px min-w-6 flex-1 bg-gradient-to-r from-copie-teal/50 to-transparent"
      />
    </div>
  );
}

const CITATION = /\[(\d+)\]/g;

// เดินไล่ children ของ markdown แล้วแทน "[n]" ที่อยู่ในสตริงด้วยปุ่มอ้างอิง
function withCitations(nodes: ReactNode, onClick: (index: number) => void, count: number): ReactNode {
  return Children.map(nodes, (node) => {
    if (typeof node === "string") return splitCitations(node, onClick, count);
    // ข้ามเนื้อหาใน element ลูก (เช่น <strong>) — ปล่อยให้ component ของมันจัดการเอง
    if (isValidElement(node)) return node;
    return node;
  });
}

function splitCitations(text: string, onClick: (index: number) => void, count: number): ReactNode {
  if (!CITATION.test(text)) return text;
  CITATION.lastIndex = 0;

  const parts: ReactNode[] = [];
  let cursor = 0;
  let match: RegExpExecArray | null;

  while ((match = CITATION.exec(text)) !== null) {
    const index = Number(match[1]);
    if (index < 1 || index > count) continue; // [9] ที่ไม่มี source จริง = ข้อความธรรมดา

    if (match.index > cursor) parts.push(text.slice(cursor, match.index));
    parts.push(
      <button
        key={`${index}-${match.index}`}
        type="button"
        onClick={() => onClick(index)}
        aria-label={`ดูแหล่งอ้างอิงที่ ${index}`}
        className="mx-0.5 inline-flex h-5 min-w-5 items-center justify-center rounded border border-copie-teal/40 bg-copie-teal/10 px-1 align-[2px] text-xs font-semibold tabular-nums text-copie-teal transition hover:bg-copie-teal/20"
      >
        {index}
      </button>,
    );
    cursor = match.index + match[0].length;
  }

  if (cursor < text.length) parts.push(text.slice(cursor));
  return parts;
}
