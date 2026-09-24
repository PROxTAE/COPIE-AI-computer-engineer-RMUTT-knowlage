## ทำอะไร
<!-- 1–3 บรรทัด: PR นี้เพิ่ม/แก้อะไร และทำไม -->

## ประเภท
- [ ] feat  - [ ] fix  - [ ] style  - [ ] refactor  - [ ] test  - [ ] data  - [ ] docs  - [ ] chore  - [ ] contract

## Module / เจ้าของ / Phase
<!-- เช่น rag (P4) — Phase 3 Hybrid search ใน 04_DEPARTMENT_RAG.md -->

## ขอบเขต
In scope:
-

Out of scope (ทำ PR ถัดไป):
-

## Dependency
<!-- ต้องรอ PR ไหน / ใครใช้ของใน PR นี้ -->

## Contract / Data / Env ที่เปลี่ยน
<!-- ไม่มี ให้ใส่ "-" -->
- Contract:
- DB / data files:
- Env vars:

## วิธีทดสอบ
```bash
# คำสั่งที่ reviewer copy ไปรันได้เลย
```

## หลักฐานว่าใช้งานได้
<!-- Frontend: screenshot/GIF · Backend: ผล curl หรือ pytest -->

## Checklist
- [ ] Branch ชื่อ `<module>/<feature>` และ base = `develop`
- [ ] ตรงตาม Contract (ไม่แก้ `contract.ts` / `contract.py` นอก `contract/*` PR)
- [ ] แก้เฉพาะโฟลเดอร์ของตัวเอง (หรือเจ้าของอนุญาตแล้ว)
- [ ] merge `origin/develop` ล่าสุดแล้ว ไม่มี conflict
- [ ] `npm run build` / `pytest` ของตัวเองผ่าน
- [ ] ไม่มี secret, ไม่มี debug print ค้าง, ไม่มี mock ใน flow จริง (หลัง Day 3)
- [ ] ไม่มีลายน้ำ AI ใน commit / PR / code และไม่มีไฟล์ของ AI tool (รัน `bash scripts/check-ai-watermark.sh --range origin/develop..HEAD` แล้ว)
- [ ] อธิบายโค้ดทุกบรรทัดใน PR นี้ได้เอง
