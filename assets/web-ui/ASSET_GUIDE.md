# COPIE Web UI Asset Kit — White Cyberism

ชุดไฟล์แยกส่วนจากทิศทางภาพ [UI Flow](../mockups/ui-flow-v1/SCREEN_GUIDE.md) สำหรับนำไปประกอบเว็บจริง ไฟล์ภาพ mockup ใช้เป็นแบบอ้างอิง ส่วนชุดนี้มีองค์ประกอบที่นำกลับมาใช้ซ้ำได้และปรับตามขนาดหน้าจอได้

## โครงสร้างโฟลเดอร์

| โฟลเดอร์ | ไฟล์ | ใช้ทำอะไร |
| --- | --- | --- |
| [brand](brand/) | copie-mark.svg, favicon.svg | เครื่องหมาย COPIE ขนาดเล็กและไอคอนแท็บเบราว์เซอร์ |
| [backgrounds](backgrounds/) | grid-light.svg | เส้นกริดฟ้าจางบนพื้นขาว |
| [backgrounds](backgrounds/) | floor-perspective.svg | เส้นพื้นลึกเฉพาะหน้าที่มาสคอตเป็นจุดเด่น |
| [backgrounds](backgrounds/) | mascot-halo.svg | วงแสงโปร่งใสหลังมาสคอต |
| [backgrounds](backgrounds/) | cyan-wash.svg | สีฟ้าอ่อนช่วงล่างของหน้าจอ |
| [frames](frames/) | corner-accent.svg | มุมเส้นสีฟ้าสำหรับกรอบพื้นที่คำตอบ หมุนใช้ได้ทั้งสี่มุม |
| [frames](frames/) | response-rule.svg | เส้นคั่นและแถบเน้นใต้หัวข้อคำตอบ |
| [frames](frames/) | side-rail.svg | เส้นแบ่งแถบด้านขวาในโหมดอ่าน ตาราง การ์ด และ Radar |
| [effects](effects/) | data-streak.svg | เส้นแสงสั้นหลังหัวข้อขณะคำตอบปรากฏ |
| [effects](effects/) | signal-dots.svg | ลายจุดสำหรับพื้นที่เล็ก ๆ ไม่ควรปูทั้งหน้า |
| [icons](icons/) | SVG 23 ชิ้น | โปรไฟล์ History ส่งข้อความ ค้นหา นำทาง แหล่งอ้างอิง Feedback และปุ่มเลือกโหมด |
| [mascot/states](mascot/states/) | PNG โปร่งใส 8 ท่า | สถานะ idle, listening, thinking, responding, success, no-answer, skill-guide และภาพหน้าตรงถือแล็ปท็อป |
| [mascot/modes](mascot/modes/) | PNG โปร่งใส 16 ภาพ | Devil Mode และ Developer Mode อย่างละ 8 สถานะ ใช้ท่าเดิมของ COPIE |
| [styles](styles/) | tokens.css, copie-ui.css, motion.css | สี ฟอนต์ กรอบ ช่องพิมพ์ ปุ่ม และแอนิเมชันที่เคารพ reduced motion |

ไฟล์ [manifest.json](manifest.json) เป็นรายการไฟล์สำหรับงานพัฒนา และ [preview.html](preview.html) เป็นหน้าเปิดดูองค์ประกอบของชุดนี้

## ชุดตกแต่งสำหรับโหมดเพิ่มเติม

ชุด Devil Mode และ Developer Mode อยู่ในโฟลเดอร์ backgrounds, frames, effects, icons และ mascot/modes เพื่อให้ `scripts/sync_ui_assets.py` คัดลอกไปใช้ได้ตามเดิม ดูไฟล์ที่ต้องใช้ สีแนะนำ และข้อควรระวังใน [MODES.md](MODES.md) หรือเปิด [mode-preview.html](mode-preview.html) เพื่อดูภาพรวม (`mode-preview.png` เป็นภาพตัวอย่างพร้อมเปิดดู) ทั้งสองชุดยังเป็นมาสคอต COPIE ตัวเดิม ท่าทางเดิม แต่เปลี่ยนไฟและเอฟเฟกต์ให้เข้ากับโหมด

## การเลือกใช้ตามหน้าจอ

| บริบท | องค์ประกอบหลัก |
| --- | --- |
| Login / Onboarding | grid-light.svg, cyan-wash.svg, มาสคอต PNG หน้าตรง; ไม่แสดงไอคอนโปรไฟล์หรือ History ก่อนเข้าสู่ระบบ |
| แชตขณะพิมพ์ | มาสคอตกลางจอ, mascot-halo.svg, floor-perspective.svg, ช่องพิมพ์, history.svg, profile.svg, send.svg |
| AI ตอบกลับ | เพิ่ม response-rule.svg และ data-streak.svg เฉพาะหัวข้อ; คำตอบยังเป็น HTML/ข้อความจริง |
| โหมดอ่านเต็ม | มาสคอตย่อไปแถบขวา, side-rail.svg, ไอคอน eye-off, copy, thumb-up, thumb-down, document |
| History | แผงลอย HTML/CSS กับไอคอน history, search, close, menu; รายการมาจากประวัติจริง |
| ตารางรายวิชา / การ์ด | ใช้เส้นและกรอบ CSS, มาสคอตขนาดเล็ก; ตารางและการ์ดสร้างจากข้อมูลจริง |
| แบบประเมิน | ใช้ฟอร์ม HTML ที่กดได้จริง, มาสคอตขนาดเล็กระหว่างตอบ; response-rule.svg ใช้กับหัวข้อ |
| Skill Radar | สร้างกราฟจากคะแนนจริงด้วย chart component, ใช้มาสคอตและเส้นตกแต่งจากชุดนี้ |

## วิธีใช้ในเว็บ

1. รัน `python scripts/sync_ui_assets.py` เพื่อคัดลอก SVG ไป `frontend/public/copie-ui/` และแปลง PNG มาสคอตเป็น WebP; อ้าง SVG เช่น `/copie-ui/icons/history.svg`
2. สคริปต์ sync คัดลอก CSS ไป `frontend/src/modules/core/theme/kit/` และแก้ URL ให้ชี้ `/copie-ui/` แล้ว; `app/globals.css` นำเข้า CSS นี้
3. ใช้ copie-ui เป็น class ของพื้นที่หน้าจอที่ใช้ธีมนี้ แล้วเลือก class ย่อย เช่น copie-halo, copie-input, copie-button, copie-mascot
4. สำหรับไอคอนที่ต้องเปลี่ยนสีด้วย CSS ให้นำ SVG ไปใช้แบบ inline หรือ CSS mask; SVG แต่ละไฟล์ใช้ currentColor
5. ใช้ WebP ที่ sync ไปใน frontend สำหรับมาสคอต 2.5D และเลือก `state` ให้ตรงกับสถานะของหน้า

ตัวอย่างโครง HTML ขั้นต่ำ:

    <main class="copie-ui">
      <div class="copie-floor"></div>
      <div class="copie-halo"></div>
      <img class="copie-mascot" src="/copie-ui/mascot/copie-front-laptop.webp" alt="COPIE" />
    </main>

## กติกาการประกอบ UI

- เว้นพื้นขาวให้มากกว่าพื้นที่ตกแต่ง เส้นกริด วงแสง และ data streak ใช้อย่างเบา
- รักษาลำดับภาพ: มาสคอตใหญ่กลางจอในหน้าแชต; ย่อหรือซ่อนเมื่อเนื้อหาต้องใช้พื้นที่
- ปุ่มและช่องกรอกควรเป็น HTML จริงพร้อม focus state
- ข้อความตอบ แหล่งอ้างอิง ตาราง การ์ด แบบประเมิน และกราฟต้องเรนเดอร์จากข้อมูลจริง
- CSS ในชุดนี้มี prefers-reduced-motion เพื่อหยุดแอนิเมชันเมื่อผู้ใช้ตั้งค่าลดการเคลื่อนไหว

PNG ต้นฉบับมาสคอตอยู่ที่ `assets/web-ui/mascot/states/`; `scripts/sync_ui_assets.py` แปลงเป็น WebP ใน `frontend/public/copie-ui/mascot/` ไฟล์ SVG/CSS ในชุดนี้สร้างเป็นองค์ประกอบใหม่ตามภาพต้นแบบ
