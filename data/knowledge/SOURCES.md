# แหล่งข้อมูลของคลังความรู้ภาควิชา (data/knowledge)

ไฟล์นี้ไม่ถูก ingest (ingest อ่านเฉพาะไฟล์ที่มี front-matter) ใช้สำหรับตรวจสอบที่มาของข้อมูล

ดึงข้อมูลและตรวจสอบเมื่อ 2026-09-25 · ผู้รับผิดชอบ P4 · ขอให้ P8 ช่วยเปิดลิงก์ตรวจเทียบเนื้อหา

## เอกสารในคลังความรู้

| doc_id | ไฟล์ | source_url หลัก | แหล่งเสริมที่อ้างใน section |
|---|---|---|---|
| ce-overview | ce-overview.md | https://cpe.engineer.rmutt.ac.th/about/ | – |
| program-structure | program-structure.md | https://engineer.rmutt.ac.th/com-course/ | https://engineer.rmutt.ac.th/computer-course/ |
| admission | admission.md | https://engineer.rmutt.ac.th/com-course/ | https://engineer.rmutt.ac.th/computer/ |
| tuition-fees | tuition-fees.md | https://engineer.rmutt.ac.th/com-course/ | https://engineer.rmutt.ac.th/computer/ |
| careers | careers.md | https://engineer.rmutt.ac.th/com-course/ | – |
| labs-facilities | labs-facilities.md | https://cpe.engineer.rmutt.ac.th/infrastructure/ | – |
| coop-internship | coop-internship.md | https://cpe.engineer.rmutt.ac.th/document/ (ไฟล์ "ข้อกำหนดสหกิจศึกษา 2568") | https://cpe.engineer.rmutt.ac.th/about/ |
| contact | contact.md | https://cpe.engineer.rmutt.ac.th/contact/ | – |
| staff | staff.md | https://cpe.engineer.rmutt.ac.th/staffs/ | – |
| faq-current-student | faq-current-student.md | https://cpe.engineer.rmutt.ac.th/document/ | หน้าปฏิทินการศึกษาของภาควิชา, https://sites.google.com/en.rmutt.ac.th/cpe-faq |
| study-plan-overview | study-plan-overview.md (จาก P5, PR #11) | หน้าดาวน์โหลด "หลักสูตร68-วิศวกรรมคอมพิวเตอร์" บน https://cpe.engineer.rmutt.ac.th/document/ | อ้างเลขหน้าในเล่มหลักสูตร 68 (หน้า 20, 30–33) |

## เอกสารต้นฉบับ (PDF) ที่ยืนยันที่มาแล้ว — ใช้ใน PR ingest ถัดไป

| ไฟล์ | ที่มา | วิธียืนยัน |
|---|---|---|
| หลักสูตร-683.pdf (หลักสูตร 68) | https://cpe.engineer.rmutt.ac.th/document/ | ชื่อรายการตรงกับหน้าเอกสารภาควิชา |
| หลักสูตร63-คอมพิวเตอร์.pdf | https://cpe.engineer.rmutt.ac.th/document/ | ชื่อรายการตรงกับหน้าเอกสารภาควิชา |
| CLOs-Computer_Engineering-RMUTT.pdf | https://cpe.engineer.rmutt.ac.th/document/ ("ผลลัพธ์การเรียนรู้ระดับรายวิชา (หลักสูตร 68)") | ชื่อรายการตรงกับหน้าเอกสารภาควิชา |
| ข้อกำหนดสหกิจศึกษา-2563.pdf, -2568.pdf | https://cpe.engineer.rmutt.ac.th/document/ | ชื่อรายการตรงกับหน้าเอกสารภาควิชา |
| forms/*.pdf (แบบฟอร์ม 01–19) | https://cpe.engineer.rmutt.ac.th/document/ | ชื่อรายการตรงกับหน้าเอกสารภาควิชา |
| คู่มือนักศึกษา69.pdf | https://oreg.rmutt.ac.th/?p=26699 | SHA-1 ตรงกับไฟล์ที่ดาวน์โหลดจาก https://oreg.rmutt.ac.th/?wpfb_dl=2598 |

## ยังไม่ใช้ / รอยืนยัน (blocker)

| รายการ | เหตุผล |
|---|---|
| Regulations-rules-and-announcements_2026-05-19.pdf | ยังไม่พบ URL ต้นทาง |
| REG-01 ถึง REG-13 (ขอสำเร็จการศึกษา, ลาพัก, ลาออก ฯลฯ) จากโปรเจกต์เดิม | เป็นเอกสารที่เรียบเรียงขึ้นใหม่ ไม่ใช่ประกาศทางการ และไม่มี URL ต้นทาง ต้องหาประกาศต้นฉบับของงานทะเบียนคณะก่อนใช้ |
| ทุนการศึกษา | ยังไม่พบแหล่งทางการ |
| รอบรับสมัคร / TCAS | ยังไม่พบประกาศรับสมัครของปีปัจจุบัน |
| กิจกรรม/ชมรม, FAQ ผู้สนใจเข้าศึกษา | ยังไม่ได้รวบรวม |

## ข้อมูลที่แหล่งต่างกันระบุไม่ตรงกัน

| เรื่อง | ค่า | ที่มา |
|---|---|---|
| ค่าเทอม | 20,000 บาท/เทอม | https://engineer.rmutt.ac.th/com-course/ (หลักสูตร 2568) |
| ค่าเทอม | 16,000 บาท (ภาคปกติ), 8,000 บาท (ฤดูร้อน) | https://engineer.rmutt.ac.th/computer/ |
| หน่วยกิตรวม | 141 | https://engineer.rmutt.ac.th/com-course/ (หลักสูตร 2568) |
| หน่วยกิตรวม | 143 | https://cpe.engineer.rmutt.ac.th/about/ (ไม่ระบุปีหลักสูตร) |

เอกสาร knowledge ระบุทั้งสองค่าพร้อมที่มา และแนะนำให้ยืนยันกับภาควิชา

## นโยบายข้อมูลบุคคล

staff.md ใส่เฉพาะชื่อ ตำแหน่ง และวิชาที่สอนตามที่เผยแพร่บนเว็บภาควิชา ไม่ใส่เบอร์โทรและอีเมลรายบุคคล ใช้เบอร์กลางภาควิชา 02 549 3460

## เอกสารที่เพิ่มในรอบ knowledge-v2

| doc_id | ไฟล์ | source_url หลัก | วิธียืนยัน |
|---|---|---|---|
| coop-internship-2563 | coop-internship-2563.md | https://cpe.engineer.rmutt.ac.th/document/ (ไฟล์ "ข้อกำหนดสหกิจศึกษา 2563") | ถอดข้อความจากภาพสแกน 2 หน้าของไฟล์ที่ภาควิชาเผยแพร่ ลงนามโดยหัวหน้าภาควิชาในขณะนั้น |
| student-projects | student-projects.md | https://cpe.engineer.rmutt.ac.th/%e0%b9%82%e0%b8%84%e0%b8%a3%e0%b8%87%e0%b8%87%e0%b8%b2%e0%b8%99%e0%b8%99%e0%b8%b1%e0%b8%81%e0%b8%a8%e0%b8%b6%e0%b8%81%e0%b8%a9%e0%b8%b2/ | สรุปจากบทคัดย่อ 10 เรื่องบนหน้าโครงงานนักศึกษา |
