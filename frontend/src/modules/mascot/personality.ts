import type { InteractionMode } from "./states";

// Small talk COPIE shows in its speech bubble when users play with it. Page-only:
// these lines are never sent to the server or saved in conversation history.
type Personality = {
  poke: string[];
  combo: string;
  pet: string;
  greet: string;
  idle: string[];
  success: string;
  // Glyphs for particle bursts and the ambient layer in front of the mascot.
  sparks: string[];
  hearts: string[];
};

export const PERSONALITY: Record<InteractionMode, Personality> = {
  normal: {
    poke: [
      "สวัสดีครับ! มีอะไรให้ COPIE ช่วยไหม",
      "จิ้มเบา ๆ นะครับ 😄",
      "พร้อมช่วยหาคำตอบเสมอครับ",
      "ลองถามเรื่องรายวิชาหรือภาควิชาดูสิครับ",
      "วันนี้อยากเรียนรู้อะไรดีครับ",
    ],
    combo: "โอ๊ะ หัวหมุนแล้วครับ 😵‍💫",
    pet: "ชอบจังครับ~ ☺️",
    greet: "กลับมาโหมดปกติแล้วครับ คุยกันสบาย ๆ",
    idle: ["ลองพิมพ์ “ปี 1 เรียนอะไรบ้าง” ดูสิครับ", "แตะผมเล่นได้นะครับ 👋", "อยากรู้ว่าตัวเองถนัดสายไหน ลองให้ผมประเมิน skill ได้ครับ"],
    success: "เยี่ยมเลยครับ! ✨",
    sparks: ["✦", "◆", "✧", "●"],
    hearts: ["♥", "♡", "✦"],
  },
  devil: {
    poke: [
      "จิ้มผมแล้วได้อะไรครับ ลองตั้งคำถามยาก ๆ ดีกว่า 😈",
      "อย่าแค่จิ้ม พิสูจน์ด้วยการลงมือสิครับ",
      "เป้าหมายวันนี้คืออะไร บอกมาให้ชัดครับ",
      "ความกลัวไม่ช่วยให้เก่งขึ้น แต่การลองช่วยได้ครับ",
      "ผมพร้อมท้าทายความคิดคุณแล้วครับ",
    ],
    combo: "พอ ๆ! เก็บพลังไว้ใช้กับโจทย์จริงเถอะครับ 🔥",
    pet: "...ก็ได้ ยอมให้ลูบหัวนิดนึง 😏",
    greet: "Devil Mode เปิดแล้ว! ผมจะท้าทายเหตุผลของคุณ แต่ไม่ดูถูกกันแน่นอนครับ",
    idle: ["ยังไม่ถามอะไรเลย กล้าลองไหมครับ?", "เลือกเรื่องที่คิดว่ายากที่สุด แล้วมาคุยกันครับ"],
    success: "ดี! แต่อย่าหยุดแค่นี้นะครับ 🔥",
    sparks: ["✦", "⚡", "♦", "✶"],
    hearts: ["♥", "♥", "✶"],
  },
  developer: {
    poke: [
      "> ping copie … pong! 🟢",
      "console.log(\"สวัสดีครับ\")",
      "พร้อม debug ไปด้วยกันครับ",
      "git commit -m \"ถามได้เลย\"",
      "ลองแยกปัญหาเป็นขั้น ๆ แล้วส่งมาครับ",
    ],
    combo: "Stack overflow! 🌀 ขอ reboot แป๊บครับ",
    pet: "mood.level++ ✅ ดีขึ้นเยอะเลยครับ",
    greet: "Developer Mode: ตอบกระชับ เป็นขั้นตอน พร้อมลุยครับ",
    idle: ["$ waiting for input_", "ลองถาม “วิชา data structure เรียนอะไร” ดูครับ"],
    success: "Build passed ✅",
    sparks: ["</>", "{ }", "01", "λ", ";"],
    hearts: ["<3", "♥", "++"],
  },
};

export function pick<T>(items: readonly T[], avoid?: T): T {
  const pool = items.length > 1 && avoid !== undefined ? items.filter((item) => item !== avoid) : items;
  return pool[Math.floor(Math.random() * pool.length)];
}
