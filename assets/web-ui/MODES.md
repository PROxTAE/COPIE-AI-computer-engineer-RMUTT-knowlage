# COPIE mode decoration kit

ชุดนี้เป็น **asset ตกแต่ง** สำหรับเปลี่ยนบรรยากาศของเว็บ โดยคงตัวละคร COPIE และท่าทางเดิม ไม่เปลี่ยนเนื้อหาคำตอบเอง โหมดปกติใช้ asset เดิมใน `ASSET_GUIDE.md`

มาสคอตแต่ละโหมดมีภาพทั้ง 8 สถานะอยู่ใน `mascot/modes/devil/states/` และ `mascot/modes/developer/states/` โดยใช้ชื่อไฟล์เดียวกับ `mascot/states/` และขนาด 1089 × 1445 พิกเซลเท่ากัน หลัง sync จะเรียกได้จาก `/copie-ui/mascot/modes/<mode>/copie-<state>.webp` เช่น `/copie-ui/mascot/modes/devil/copie-thinking.webp` ภาพ `copie-front-laptop` ใช้กับสถานะ `welcome`

เปิด `mascot/modes/states-preview.html` หรือภาพ `mascot/modes/states-preview.png` เพื่อเทียบทั้ง 8 สถานะในสามโหมด ภาพโหมดใหม่สร้างด้วย built-in imagegen โดยใช้ภาพสถานะเดิมเป็น edit target และภาพ idle โหมดเดียวกันเป็น style reference; พรอมป์ต์กำหนดให้รักษารูปทรง ท่า เครื่องแต่งกาย ตรา และพื้นหลังโปร่งใส แล้วเปลี่ยนเฉพาะสีไฟดวงตา/หูฟัง แสงขอบ และอนุภาคเล็ก ๆ: Devil เป็น magenta-violet, Developer เป็น mint-teal/cyan

| โหมด | พื้นหลัง | วงแสงหลัง COPIE | มุมกรอบ | เส้นประกอบคำตอบ | ไอคอน |
| --- | --- | --- | --- | --- | --- |
| ปกติ | `backgrounds/grid-light.svg` | `backgrounds/mascot-halo.svg` | `frames/corner-accent.svg` | `effects/data-streak.svg` | `brand/copie-mark.svg` |
| Devil | `backgrounds/devil-grid.svg` | `backgrounds/devil-halo.svg` | `frames/devil-corner.svg` | `effects/devil-energy.svg` | `icons/mode-devil.svg` |
| Developer | `backgrounds/developer-grid.svg` | `backgrounds/developer-halo.svg` | `frames/developer-corner.svg` | `effects/developer-signal.svg` | `icons/mode-developer.svg` |

## สีแนะนำเมื่อทำ theme ในเว็บ

| โหมด | พื้น | ข้อความหลัก | สีเน้น | เส้นกรอบ |
| --- | --- | --- | --- | --- |
| ปกติ | `#FFFFFF` | `#111A30` | `#155FF2` | `#D7E5F8` |
| Devil | `#0C1023` | `#F8F3FF` | `#F66CAC` | `#634567` |
| Developer | `#081820` | `#E8FFF8` | `#65E8D6` | `#35656C` |

## การใช้งาน

1. รัน `python scripts/sync_ui_assets.py` เพื่อคัดลอก SVG ไปที่ `frontend/public/copie-ui/` เช่น `/copie-ui/backgrounds/devil-grid.svg`.
2. ใช้พื้นหลังโหมดเป็นเลเยอร์หลังสุด; วาง halo หลัง COPIE; วาง frame และ effect เฉพาะบางตำแหน่งเพื่อไม่ให้แย่งความสนใจจากเนื้อหา.
3. เปลี่ยนสีข้อความ ฟอร์ม ปุ่ม focus และพื้นการ์ดด้วย CSS ของหน้าเว็บตามตารางสีข้างบน เพราะ SVG เหล่านี้เป็นงานตกแต่ง ไม่ได้เปลี่ยน theme ทั้งหน้าให้เอง.
4. ใช้ไอคอนโหมดในปุ่ม HTML จริง พร้อมชื่อโหมดที่อ่านได้. SVG ไอคอนใช้ `currentColor` เพื่อปรับสีผ่าน CSS.

ภาพทั้งหมดเป็น SVG ที่ขยายตามหน้าจอได้และไม่มีข้อความฝังในภาพ เปิด `mode-preview.html` เพื่อดูทั้งสามโหมดก่อนนำไปต่อกับระบบสลับโหมด.
