// Public API of the "renderer" module (P6).
// Other modules import only from "@/modules/renderer".
export { ResponseRenderer } from "./ResponseRenderer";
export type { ResponseRendererProps, AssessmentAnswer } from "./ResponseRenderer";
export { DevPlayground } from "./DevPlayground";
// MOCKS ใช้ได้เฉพาะ /dev และ tests — หลัง M3 ห้าม import ใน flow /chat
export { MOCKS, MOCK_LABELS, type MockKey } from "./mock";
