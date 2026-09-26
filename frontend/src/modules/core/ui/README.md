# Core UI (P1)

ใช้ `AppHeader`, `StatusLabel`, `HistoryButton`, `ChatInput` และ `Icon` ผ่าน `@/modules/core` หลัง PR `core/ui-shell` merge แล้ว ทุก component ใช้ token จาก White Cyberism ที่ `app/globals.css` โหลดไว้

```tsx
<AppHeader profile={profileControl} />
<HistoryButton onPress={openHistory} />
<ChatInput onSend={send} pending={pending} />
<Icon name="document" label="เอกสาร" />
```

`AppHeader.profile` เป็น slot ให้ P2 ใส่ปุ่มโปรไฟล์จริง `HistoryButton` ต้องมี handler จาก P2 ส่วน `ChatInput` ส่งข้อความที่ trim แล้วสูงสุด 1000 ตัวอักษร: Enter ส่ง, Shift+Enter ขึ้นบรรทัดใหม่ และปิดปุ่มระหว่าง pending

`Icon` ใช้ CSS mask ของ SVG ใน `/copie-ui/icons/`; สีตาม `currentColor` จึงเปลี่ยนผ่าน `text-cyber-*` ได้

`core/api.ts` เรียก endpoint ตาม `contract.ts`; ก่อนใช้ endpoint ที่ต้อง auth ให้ P2 เรียก `configureApiAuth({ getToken, clearToken, onUnauthorized })` ฝั่ง client และเรียก `notifyApiAuthChanged()` หลัง login/logout หรือ token เปลี่ยน โดย `onUnauthorized` นำผู้ใช้ไป `/login` ผ่าน Next router. ระหว่างที่ P2 ยังไม่เชื่อม หน้า `/chat` จะปิด input/history และไม่ส่งข้อความจำลอง
