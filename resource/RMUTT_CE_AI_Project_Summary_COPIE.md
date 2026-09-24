# Project Summary: RMUTT Computer Engineering AI Assistant

> **Mini Project ระยะเวลา 5 วัน / ทีม 8 คน**  
> ระบบ AI Assistant สำหรับ **ภาควิชาวิศวกรรมคอมพิวเตอร์ มหาวิทยาลัยเทคโนโลยีราชมงคลธัญบุรี (RMUTT)**  
> โดยเน้นการให้ข้อมูลเกี่ยวกับภาควิชา หลักสูตร รายวิชา นักศึกษา และการวิเคราะห์ทักษะของผู้ใช้งาน ผ่านประสบการณ์แบบ **3D AI Mascot **COPIE** **COPIE** **COPIE** + Dynamic UI** แทน Chatbot แบบข้อความทั่วไป

---

# 1. แนวคิดของโครงการ

ระบบ **RMUTT Computer Engineering AI Assistant** เป็นระบบผู้ช่วย AI ที่ออกแบบมาโดยเฉพาะสำหรับข้อมูลของ **ภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT**

ระบบไม่ได้มีเป้าหมายเป็น AI สำหรับข้อมูลทั้งมหาวิทยาลัย แต่จำกัดขอบเขตหลักไว้ที่ข้อมูลที่เกี่ยวข้องกับภาควิชาวิศวกรรมคอมพิวเตอร์ เช่น

- ข้อมูลเกี่ยวกับภาควิชาวิศวกรรมคอมพิวเตอร์
- ข้อมูลหลักสูตร
- แผนการเรียน
- รายวิชาและหน่วยกิต
- รายละเอียดรายวิชา
- ข้อมูลที่นักเรียนก่อนเข้าศึกษาควรรู้
- ข้อมูลสำหรับนักศึกษาปัจจุบัน
- การประเมิน Skill Profile
- การเก็บประวัติการใช้งาน
- การเก็บ Feedback ต่อคำตอบของ AI

จุดเด่นของระบบคือ ผู้ใช้จะไม่ได้ใช้งานผ่าน Chatbot แบบกล่องข้อความเพียงอย่างเดียว แต่จะพูดคุยกับ **AI Mascot **COPIE** แบบ 3D** และ AI Agent จะสามารถตัดสินใจได้เองว่า

1. คำถามของผู้ใช้ต้องใช้ข้อมูลหรือ Tool ใด
2. ระบบมีข้อมูลเพียงพอหรือไม่
3. หากข้อมูลไม่พอ ควรขอข้อมูลเพิ่มเติมจากผู้ใช้อย่างไร
4. คำตอบควรแสดงผลในรูปแบบใด เช่น Text, Table, Card, Form หรือ Chart

---

## 1.1 ชื่อมาสคอตของระบบ

มาสคอต AI หลักของระบบมีชื่อว่า **COPIE**

COPIE เป็นตัวแทนของ AI Assistant ประจำภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT และเป็นตัวละครหลักที่ผู้ใช้จะโต้ตอบด้วยบนหน้า Main AI Experience

บทบาทของ COPIE ได้แก่

- เป็นจุดศูนย์กลางของประสบการณ์การใช้งาน
- แสดงสถานะของ AI เช่น Idle, Thinking, Responding และ Success
- รับคำถามจากผู้ใช้
- แสดงผลร่วมกับ Dynamic UI เช่น Table, Card, Assessment Form และ Skill Radar
- ทำหน้าที่เป็นภาพจำหลักของระบบ

---

# 2. เป้าหมายของระบบ

## 2.1 เป้าหมายหลัก

พัฒนาระบบ AI Assistant ที่ช่วยให้ผู้ใช้งานสามารถเข้าถึงและทำความเข้าใจข้อมูลของภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT ได้ง่ายขึ้น

ระบบควรสามารถ

- ตอบคำถามจากฐานข้อมูลหรือเอกสารของภาควิชา
- แสดงข้อมูลหลักสูตรในรูปแบบที่อ่านง่าย
- เข้าใจบริบทของผู้ใช้งานแต่ละประเภท
- วิเคราะห์ Skill Profile ของผู้ใช้
- เลือกรูปแบบการแสดงผลให้เหมาะกับคำถาม
- เก็บประวัติการสนทนา
- เก็บ Feedback เพื่อนำไปปรับปรุงระบบ

---

# 3. กลุ่มผู้ใช้งานเป้าหมาย

ระบบแบ่งกลุ่มผู้ใช้งานหลักออกเป็น 4 กลุ่ม

## 3.1 ผู้ที่สนใจเข้าศึกษา

ผู้ใช้งานที่ยังไม่ได้เป็นนักศึกษาของภาควิชา และต้องการข้อมูล เช่น

- ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร
- หลักสูตรมีโครงสร้างอย่างไร
- แต่ละปีเรียนอะไร
- รายวิชาหลักมีอะไรบ้าง
- ทักษะที่เหมาะกับการเรียนวิศวกรรมคอมพิวเตอร์มีอะไรบ้าง

## 3.2 นักศึกษาชั้นปีต้น

เช่น นักศึกษาปี 1 หรือปี 2

อาจใช้ระบบเพื่อ

- ตรวจสอบรายวิชา
- ดูแผนการเรียน
- ดูจำนวนหน่วยกิต
- สอบถามรายละเอียดวิชา
- ทำ Skill Assessment เพื่อสำรวจความถนัด

## 3.3 นักศึกษาระหว่างเรียน

เช่น นักศึกษาปี 2 หรือปี 3

อาจใช้ระบบเพื่อ

- ค้นหารายวิชา
- ดูรายละเอียดวิชาที่กำลังจะเรียน
- วิเคราะห์ Skill Profile
- ดูความสัมพันธ์ระหว่างทักษะกับเนื้อหาที่เรียน
- ถามคำถามเฉพาะเกี่ยวกับหลักสูตร

## 3.4 นักศึกษาใกล้สำเร็จการศึกษา

อาจใช้ระบบเพื่อ

- สรุปสิ่งที่เรียนมา
- สรุป Skill Profile
- ตรวจสอบรายวิชาที่ผ่านมา
- ดูข้อมูลประกอบการวางแผนพัฒนาทักษะต่อไป

> หมายเหตุ: ใน Mini Project นี้ **Career & Learning Roadmap แบบเต็มรูปแบบยังไม่อยู่ใน Core Scope** เพื่อควบคุมขนาดงานให้สามารถพัฒนาได้ภายใน 5 วัน

---

# 4. User Flow หลักของระบบ

```text
เข้าสู่ระบบด้วย Google
        ↓
ตรวจสอบว่าเป็นผู้ใช้ใหม่หรือไม่
        ↓
ถ้าเป็นผู้ใช้ใหม่
        ↓
Onboarding / User Profile
        ↓
ระบุ
- ชื่อ
- ช่วงอายุ
- สถานะผู้ใช้งาน
- ชั้นปี (ถ้าเป็นนักศึกษา)
        ↓
เข้าสู่ Main AI Experience
        ↓
พูดคุยกับ 3D AI Mascot **COPIE** **COPIE**
        ↓
AI Agent วิเคราะห์คำถาม
        ↓
ตรวจสอบ User Context
        ↓
เลือก Tool ที่เหมาะสม
        ↓
ประมวลผล
        ↓
เลือก Response Format
        ↓
Dynamic UI Renderer
        ↓
แสดงคำตอบ
        ↓
บันทึก History + Feedback
```

---

# 5. Login และ User Onboarding

## 5.1 Google Sign-In

ระบบใช้ Google Account สำหรับเข้าสู่ระบบ

Flow:

```text
Continue with Google
        ↓
Google Authentication
        ↓
ตรวจสอบ User
        ↓
Existing User → Main System
New User      → Onboarding
```

ข้อมูลพื้นฐานจาก Google ที่สามารถใช้ได้ เช่น

- Name
- Email
- Profile Image

## 5.2 Onboarding

ผู้ใช้ใหม่จะทำแบบสอบถามสั้น ๆ เพื่อให้ AI เข้าใจบริบทของผู้ใช้

ข้อมูลที่เก็บ เช่น

### ข้อมูลพื้นฐาน

- ชื่อที่ต้องการให้ระบบเรียก
- ช่วงอายุ

ตัวอย่างช่วงอายุ

- ต่ำกว่า 18 ปี
- 18–20 ปี
- 21–23 ปี
- 24 ปีขึ้นไป

### สถานะผู้ใช้

- สนใจข้อมูลภาควิชาวิศวกรรมคอมพิวเตอร์
- นักศึกษาภาควิชาวิศวกรรมคอมพิวเตอร์
- นักศึกษาใกล้สำเร็จการศึกษา

หากเป็นนักศึกษาปัจจุบัน

- ปี 1
- ปี 2
- ปี 3
- ปี 4 หรือสูงกว่า

ตัวอย่าง User Profile

```json
{
  "display_name": "Tae",
  "age_range": "21-23",
  "user_type": "current_student",
  "study_year": 3
}
```

ข้อมูลนี้จะถูกใช้เป็น Context ประกอบการตอบของ AI

---

# 6. Main AI Experience

หลังเข้าสู่ระบบ ผู้ใช้จะเข้าสู่หน้าหลักที่มี **3D AI Mascot **COPIE** **COPIE****

แนวคิดหลักคือไม่ให้หน้าจอมีลักษณะเหมือน Chatbot ทั่วไป

ตัวอย่าง Layout

```text
┌─────────────────────────────────────────────────┐
│ CE AI                                User       │
│                                                 │
│                                                 │
│                  [ 3D AI ]                      │
│                   Mascot                        │
│                                                 │
│          "วันนี้อยากให้ช่วยเรื่องอะไร?"            │
│                                                 │
│   ┌─────────────────────────────────────────┐   │
│   │ Ask about Computer Engineering...      │   │
│   └─────────────────────────────────────────┘   │
│                                                 │
│   Curriculum   My Skills   Department Info      │
└─────────────────────────────────────────────────┘
```

AI Mascot **COPIE** สามารถมี Animation State เช่น

- Idle
- Listening
- Thinking
- Responding
- Success

เพื่อเพิ่มความรู้สึกว่าผู้ใช้กำลังพูดคุยกับ Assistant จริง ๆ

---

# 7. AI Agent

AI Agent เป็นสมองหลักที่ตัดสินใจว่าแต่ละคำถามต้องดำเนินการอย่างไร

## 7.1 Agent Flow

```text
User Question
      ↓
Intent Analysis
      ↓
Read User Context
      ↓
Do we have enough information?
      ↓
Choose Tool
      ↓
Execute Tool
      ↓
Generate Structured Response
      ↓
Choose UI Format
```

## 7.2 ตัวอย่างการตัดสินใจของ Agent

### กรณีที่ 1

User:

> ปี 2 เทอม 1 ต้องเรียนอะไรบ้าง

Agent:

```json
{
  "tool": "curriculum_tool",
  "action": "get_courses",
  "parameters": {
    "year": 2,
    "semester": 1
  },
  "response_type": "course_table"
}
```

### กรณีที่ 2

User:

> ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร

Agent:

```json
{
  "tool": "department_rag",
  "action": "search",
  "response_type": "text_with_sources"
}
```

### กรณีที่ 3

User:

> ช่วยสรุป Skill ของผมหน่อย

หากระบบยังไม่มี Skill Profile

Agent:

```json
{
  "tool": "skill_assessment",
  "action": "request_assessment",
  "response_type": "assessment_form"
}
```

หลังผู้ใช้ทำ Assessment แล้ว

```text
Assessment
    ↓
Calculate Score
    ↓
Save Skill Profile
    ↓
Agent Continue
    ↓
Skill Radar
```

---

# 8. Core Tools ของ AI Agent

## 8.1 Department RAG Tool

RAG จะใช้ค้นหาข้อมูลจากเอกสารของ **ภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT**

ตัวอย่างข้อมูล

- ข้อมูลภาควิชา
- หลักสูตร
- Course Description
- เอกสารหรือข้อมูลเกี่ยวกับแผนการเรียน
- FAQ
- ข้อมูลสำหรับผู้สนใจเข้าศึกษา
- เอกสารอื่น ๆ ที่อยู่ใน Scope ของภาควิชา

Pipeline

```text
Department Documents
        ↓
Extract / Clean
        ↓
Chunk
        ↓
Embedding
        ↓
Vector Database
        ↓
Retrieval
        ↓
Relevant Context + Source
```

## 8.2 Curriculum Tool

ข้อมูลที่เป็นโครงสร้างแน่นอน เช่น

- ชั้นปี
- ภาคการศึกษา
- รหัสวิชา
- ชื่อวิชา
- จำนวนหน่วยกิต

ควรเก็บเป็น Structured Data

ตัวอย่าง

```json
{
  "year": 2,
  "semester": 1,
  "courses": [
    {
      "code": "XXXXX",
      "name": "Data Structures",
      "credits": 3
    }
  ]
}
```

ไม่ควรให้ LLM เดาข้อมูลประเภทนี้เอง

## 8.3 Skill Assessment Tool

Skill Assessment เป็น Tool ที่ Agent สามารถเรียกใช้เมื่อจำเป็น

ตัวอย่าง Skill Category

- Frontend
- Backend
- Network
- Embedded / IoT
- AI / Data
- Cybersecurity

Assessment อาจมีประมาณ 8–12 คำถาม

หลังตอบครบ ระบบจะใช้ Formula คำนวณคะแนน

ตัวอย่าง

```json
{
  "frontend": 82,
  "backend": 74,
  "network": 63,
  "embedded": 48,
  "ai_data": 77,
  "cybersecurity": 55
}
```

LLM ใช้สำหรับ

- อธิบายผล
- สรุปจุดเด่น
- อธิบายความหมายของคะแนน

LLM **ไม่ควรเป็นผู้สุ่มคะแนนโดยตรง**

---

# 9. Dynamic Response System

AI จะไม่ตอบทุกอย่างเป็นข้อความ

Agent ต้องเลือก Response Format ที่เหมาะสม

รูปแบบหลักที่กำหนดไว้สำหรับ Mini Project มีดังนี้

## 9.1 Text Response

ใช้กับคำถามทั่วไป

```text
response_type = "text"
```

## 9.2 Table Response

ใช้กับข้อมูลเชิงโครงสร้าง เช่น

- รายวิชา
- หน่วยกิต
- ตารางเปรียบเทียบ

```text
response_type = "course_table"
```

## 9.3 Card Response

ใช้กับข้อมูลที่ต้องการแบ่งเป็นหมวดหมู่

```text
response_type = "cards"
```

## 9.4 Assessment Form

เมื่อ Agent ต้องการข้อมูลเพิ่มเติม

```text
response_type = "assessment_form"
```

## 9.5 Skill Radar

ใช้แสดง Skill Profile

```text
response_type = "skill_radar"
```

## 9.6 Source Viewer

ใช้แสดงเอกสารหรือแหล่งข้อมูลที่ RAG ใช้ในการตอบ

```text
response_type = "source_viewer"
```

---

# 10. Response Schema กลาง

Person 1, Person 3, Person 5 และ Person 6 ต้องตกลง Schema นี้ก่อนเริ่มพัฒนา

ตัวอย่าง

```json
{
  "message": "นี่คือรายวิชาของปี 2 เทอม 1",
  "response_type": "course_table",
  "data": {},
  "sources": [],
  "actions": []
}
```

กรณีต้องทำ Assessment

```json
{
  "message": "ผมยังไม่มีข้อมูล Skill ของคุณ",
  "response_type": "skill_assessment",
  "data": {
    "questions": []
  },
  "sources": [],
  "actions": []
}
```

---

# 11. User History

ระบบต้องบันทึก Conversation History

ตัวอย่าง

```text
Today

- ปี 3 ต้องเรียนอะไร?
- วิชา Network เรียนเกี่ยวกับอะไร?
- ช่วยวิเคราะห์ Skill ของผม
```

ข้อมูลที่ควรเก็บ

- Conversation ID
- User ID
- User message
- AI response
- Response type
- Timestamp

นอกจากนี้สามารถบันทึก Skill Assessment History ได้

---

# 12. Feedback System

ทุกคำตอบของ AI สามารถมี Feedback

```text
คำตอบนี้มีประโยชน์หรือไม่?

👍    👎
```

หากกด 👎 สามารถเลือกเหตุผล เช่น

- ข้อมูลไม่ถูกต้อง
- ไม่ตรงกับคำถาม
- อ่านยาก
- ข้อมูลไม่ครบ
- อื่น ๆ

ข้อมูล Feedback ใช้สำหรับประเมินคุณภาพของระบบในอนาคต

---

# 13. Architecture ภาพรวม

```text
                        USER
                          │
                          ▼
                 Google Authentication
                          │
                          ▼
                    User Profile
                          │
                          ▼
                ┌──────────────────┐
                │  Main Frontend   │
                │ + 3D AI Mascot **COPIE** **COPIE**   │
                └────────┬─────────┘
                         │
                         ▼
                ┌──────────────────┐
                │    AI Agent      │
                │  Intent Router   │
                └────────┬─────────┘
                         │
        ┌────────────────┼──────────────────┐
        │                │                  │
        ▼                ▼                  ▼
 Department RAG   Curriculum Tool   Skill Assessment
        │                │                  │
        └────────────────┼──────────────────┘
                         │
                         ▼
               Structured Response
                         │
                         ▼
              Dynamic UI Renderer
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
        Text           Table          Chart
        Card           Form           Source
                         │
                         ▼
                History / Feedback
```

---

# 14. การแบ่งงานทีม 8 คน

# Person 1 — Tech Lead + Main Frontend + 3D AI Mascot **COPIE** **COPIE**

## Role

**Frontend Tech Lead / 3D Experience Owner**

Person 1 เป็นผู้ดูแลภาพรวมทางเทคนิคของ Frontend และเป็นเจ้าของ Main User Experience ของระบบ

Person 1 ไม่ควรรับ Backend หลัก เพื่อให้สามารถโฟกัสกับจุดขายของระบบคือ 3D AI Interface

## Responsibilities

### Frontend Architecture

- สร้าง Project Frontend
- กำหนด Folder Structure
- กำหนด Component Structure
- กำหนด State Management
- กำหนด API integration pattern
- กำหนด Design System ร่วมกับทีม

### Main UI

พัฒนา

- Login screen integration
- Main layout
- Navigation
- Main AI workspace
- User profile access
- Responsive layout

### 3D AI Mascot **COPIE** **COPIE**

รับผิดชอบ

- 3D Scene
- AI Mascot **COPIE**
- Camera
- Lighting
- Environment
- Animation State

State ขั้นต่ำ

- Idle
- Thinking
- Responding
- Success

### Frontend Integration

เชื่อม

- Dynamic Renderer
- User module
- Agent API
- History
- Feedback

### Tech Lead

- Review Pull Request
- แก้ Integration Conflict
- กำหนด Coding Convention
- Merge Core Modules
- ดู Final Frontend Build

## Deliverables

- Main Frontend
- 3D AI Scene
- Main Workspace
- Shared UI Layout
- Frontend integration
- Final UI polish

## Timeline

### Day 1
- Project setup
- Frontend architecture
- Design system
- Main layout

### Day 2
- 3D Scene
- Mascot
- Basic animation

### Day 3
- Main AI workspace
- Input interaction
- COPIE state management

### Day 4
- Integrate Agent API
- Integrate Dynamic Renderer
- Integrate User System

### Day 5
- Responsive
- Animation polish
- Bug fix
- Final merge

**Workload: High**

---

# Person 2 — Authentication + User Profile + History + Feedback

## Role

**User System Developer**

รับผิดชอบระบบที่เกี่ยวข้องกับ User ทั้งหมด

## Responsibilities

### Google Authentication

- Google Sign-In
- User session
- Login / Logout
- ตรวจสอบ New User / Existing User

### Onboarding

สร้าง Onboarding Form

ข้อมูล

- Display Name
- Age Range
- User Type
- Study Year

### User Profile

สร้าง User Profile Model

ตัวอย่าง

```json
{
  "id": "user-id",
  "display_name": "Tae",
  "email": "example@gmail.com",
  "age_range": "21-23",
  "user_type": "current_student",
  "study_year": 3
}
```

### Conversation History

พัฒนา

- Save conversation
- Load conversation
- Conversation list
- Continue previous conversation

### Skill Profile Storage

บันทึกผล Skill Assessment ของ User

### Feedback

พัฒนา

- Like
- Dislike
- Feedback reason
- Save feedback

## Deliverables

- Google Login
- Onboarding
- User Profile
- Conversation History
- Skill History
- Feedback System

## Timeline

### Day 1
- Authentication
- User database/schema

### Day 2
- Onboarding
- User profile

### Day 3
- Conversation History

### Day 4
- Feedback
- Skill Profile Storage

### Day 5
- Integration
- Bug fix

**Workload: Medium–High**

---

# Person 3 — AI Agent + Backend Router

## Role

**AI Agent / Backend Developer**

เป็นผู้ดูแลสมองกลางของระบบ

## Responsibilities

### Backend API

สร้าง Backend Endpoint หลัก

ตัวอย่าง

```text
POST /api/chat
POST /api/agent
POST /api/assessment
```

### Intent Detection

Agent ต้องแยก Intent เช่น

- Department Information
- Curriculum
- Skill Assessment
- General Question

### Tool Selection

Agent เลือก Tool เช่น

```text
Department RAG
Curriculum Tool
Skill Assessment
User Context
General LLM
```

### Context Awareness

ใช้ข้อมูลจาก User Profile เช่น

- User Type
- Study Year
- Existing Skill Profile

### Missing Information Detection

Agent ต้องรู้ว่าเมื่อใดควรถามข้อมูลเพิ่ม

ตัวอย่าง

```text
User:
"ช่วยวิเคราะห์ Skill ของผม"

Skill Profile = NULL

Agent:
→ Request Skill Assessment
```

### Structured Output

Agent ต้องคืน JSON ที่ตรงกับ Response Schema

### Multi-step Flow

รองรับ Flow เช่น

```text
Ask Skill
   ↓
No Skill Data
   ↓
Assessment
   ↓
Save Result
   ↓
Continue Original Request
```

## Deliverables

- Backend API
- Agent Router
- Tool Calling
- Structured Output
- Context Awareness
- Multi-step Agent Flow

## Timeline

### Day 1
- Backend setup
- Agent design
- Tool schema

### Day 2
- LLM integration
- Intent router

### Day 3
- Tool calling

### Day 4
- User context
- Multi-step flow

### Day 5
- Prompt tuning
- Integration testing

**Workload: High**

---

# Person 4 — Department RAG + Knowledge Base

## Role

**RAG / Knowledge Engineer**

ดูแลข้อมูลความรู้เฉพาะของภาควิชาวิศวกรรมคอมพิวเตอร์ RMUTT

## Responsibilities

### Document Collection

รวบรวมข้อมูล เช่น

- ข้อมูลภาควิชา
- หลักสูตร
- Course Description
- FAQ
- แผนการเรียน
- เอกสารที่เกี่ยวข้องกับภาควิชา

### Data Cleaning

- ลบข้อความซ้ำ
- จัด Heading
- ตรวจความถูกต้อง
- แยก Metadata

### Chunking

กำหนดวิธี Chunk เอกสาร

### Embedding

สร้าง Vector Embedding

### Vector Database

ใช้ เช่น

- FAISS
- Chroma

### Retrieval

สร้าง Function เช่น

```text
search_department_knowledge(query)
```

### Source / Citation

ทุก Retrieval ควรส่ง Metadata กลับ เช่น

- Document name
- Page
- Section

## Deliverables

- Department Knowledge Base
- Vector DB
- Retrieval API / Function
- Source metadata
- Test query set

## Timeline

### Day 1
- Collect data
- Clean data

### Day 2
- Chunk
- Embedding
- Vector DB

### Day 3
- Retriever

### Day 4
- Source metadata
- Agent integration

### Day 5
- Test
- Improve retrieval

**Workload: Medium–High**

---

# Person 5 — Curriculum Tool + Skill Assessment Tool

## Role

**Structured Data / Assessment Developer**

รับผิดชอบ Tool ที่ใช้ข้อมูลแบบ Structured

## Responsibilities

### Curriculum Tool

สร้าง Dataset สำหรับหลักสูตร

ข้อมูล เช่น

- Year
- Semester
- Course Code
- Course Name
- Credit

สร้าง Function เช่น

```text
get_courses(year, semester)
get_course_detail(course_code)
get_total_credits(year, semester)
```

### Skill Assessment

ออกแบบคำถามประมาณ 8–12 ข้อ

Skill Category เช่น

- Frontend
- Backend
- Network
- Embedded / IoT
- AI / Data
- Cybersecurity

### Scoring

สร้าง Formula สำหรับคำนวณ Score

### Result

คืนผลแบบ Structured Data

```json
{
  "frontend": 82,
  "backend": 74,
  "network": 63,
  "embedded": 48,
  "ai_data": 77,
  "cybersecurity": 55
}
```

### Agent Integration

Agent สามารถเรียก

```text
start_skill_assessment()
calculate_skill()
get_curriculum()
```

## Deliverables

- Curriculum Dataset
- Curriculum Functions
- Assessment Questions
- Scoring Logic
- Skill Result API / Function

## Timeline

### Day 1
- Curriculum dataset

### Day 2
- Curriculum functions

### Day 3
- Skill questions
- Scoring formula

### Day 4
- Tool integration

### Day 5
- Test
- Fix data

**Workload: Medium**

---

# Person 6 — Dynamic Response Renderer

## Role

**Dynamic UI / Visualization Developer**

Person 6 ดูแลระบบที่เปลี่ยน Structured AI Response ให้กลายเป็น UI

## Responsibilities

สร้าง

```text
<ResponseRenderer />
```

ตรวจสอบ

```text
response_type
```

แล้วเลือก Component

## Components ขั้นต่ำ

### TextResponse

สำหรับคำตอบทั่วไป

### CourseTable

สำหรับรายวิชาและหน่วยกิต

### InfoCard

สำหรับข้อมูลที่แบ่งเป็นหมวดหมู่

### AssessmentForm

สำหรับแบบประเมินที่ Agent เรียก

### SkillRadar

แสดง Skill Profile

### SourceViewer

แสดงแหล่งข้อมูลจาก Department RAG

## ตัวอย่าง Logic

```text
response_type = text
→ TextResponse

response_type = course_table
→ CourseTable

response_type = skill_assessment
→ AssessmentForm

response_type = skill_radar
→ SkillRadar
```

## Deliverables

- Response Renderer
- Text UI
- Table UI
- Card UI
- Assessment UI
- Radar Chart
- Source Viewer

## Timeline

### Day 1
- Renderer architecture

### Day 2
- Text
- Table
- Card

### Day 3
- Assessment Form
- Radar Chart

### Day 4
- Source Viewer
- Animation
- Integration

### Day 5
- Responsive
- Polish
- Bug fix

**Workload: Medium–High**

---

# Person 7 — Suggested Question Buttons

## Role

**Optional UI Feature**

งานนี้ตั้งใจให้เป็นงานที่ง่ายและไม่เป็น Dependency ของระบบ

## Feature

เพิ่ม Suggested Question Buttons บริเวณหน้า AI

ตัวอย่างสำหรับผู้สนใจเข้าศึกษา

```text
[ ภาควิชานี้เรียนอะไร? ]
[ หลักสูตรมีอะไรบ้าง? ]
[ แต่ละปีเรียนอะไร? ]
```

สำหรับนักศึกษาปัจจุบัน

```text
[ เทอมนี้ต้องเรียนอะไร? ]
[ ดู Skill ของฉัน ]
[ อธิบายรายวิชา ]
```

สามารถเปลี่ยนตาม User Type ได้

## Implementation

ข้อมูลสามารถเก็บในไฟล์ Frontend เช่น

```text
suggested-prompts.ts
```

ไม่ต้องสร้าง Backend ใหม่

## Deliverables

- Prompt configuration
- Suggested prompt component
- Role-based prompt selection

## Estimated Time

**2–4 ชั่วโมง**

**Workload: Very Low**

หาก Person 7 ไม่สามารถทำได้ สามารถถอด Feature นี้ออกได้ทันทีโดยไม่กระทบ Core System

---

# Person 8 — Copy Response / Simple Export

## Role

**Optional Utility Feature**

เป็น Feature ที่ง่ายและไม่เป็น Dependency

## Feature 1: Copy Answer

เพิ่มปุ่ม

```text
[ Copy ]
```

ใน AI Response

ใช้ Browser Clipboard API

## Feature 2: Export Text

หากมีเวลาเพิ่ม สามารถ Export Conversation เป็น

- TXT
- JSON

ตัวอย่าง

```text
[ Copy ]
[ Export ]
```

## Deliverables

ขั้นต่ำ

- Copy Response

ถ้ามีเวลา

- Export TXT
- Export JSON

## Estimated Time

**1–3 ชั่วโมง**

**Workload: Very Low**

หาก Person 8 ไม่สามารถทำ Feature ได้ ระบบหลักยังทำงานครบทั้งหมด

---

# 15. ตารางสรุป Team Assignment

| Person | Main Responsibility | Priority | Workload |
|---|---|---|---|
| 1 | Tech Lead + Main Frontend + 3D AI | Core | High |
| 2 | Auth + User + History + Feedback | Core | Medium–High |
| 3 | AI Agent + Backend Router | Core | High |
| 4 | Department RAG + Knowledge | Core | Medium–High |
| 5 | Curriculum + Skill Assessment | Core | Medium |
| 6 | Dynamic Response Renderer | Core | Medium–High |
| 7 | Suggested Questions | Optional | Very Low |
| 8 | Copy / Simple Export | Optional | Very Low |

---

# 16. 5-Day Development Plan

| Person | Day 1 | Day 2 | Day 3 | Day 4 | Day 5 |
|---|---|---|---|---|---|
| P1 | Frontend Architecture | 3D Mascot | Main Workspace | Integration | Polish |
| P2 | Auth + Schema | Onboarding | History | Feedback | Integration |
| P3 | Agent Architecture | LLM + Router | Tool Calling | Context | Tune/Test |
| P4 | Documents | Vector DB | Retrieval | Source | Test |
| P5 | Curriculum Data | Curriculum Tool | Skill Logic | Integration | Test |
| P6 | Renderer Core | Table/Card | Form/Radar | Source/Integration | Polish |
| P7 | Suggested Prompt | Optional Fix | - | - | - |
| P8 | Copy/Export | Optional Fix | - | - | - |

---

# 17. Critical Dependency

Core System ต้องไม่ขึ้นอยู่กับ Person 7 และ Person 8

```text
Person 1 → Main UI
Person 2 → User System
Person 3 → AI Agent
Person 4 → Department RAG
Person 5 → Curriculum / Skill
Person 6 → Dynamic Renderer

Person 7 → Optional
Person 8 → Optional
```

ต่อให้ Person 7 และ Person 8 ไม่มีเวลาทำ ระบบยังต้องสามารถ Demo ได้ครบ

---

# 18. Day 1 Contract Freeze

ก่อนแยกกันพัฒนา Person 1, 2, 3, 5 และ 6 ต้องตกลงเรื่องต่อไปนี้ให้เรียบร้อย

## API Contract

ตัวอย่าง

```text
POST /api/chat
POST /api/assessment
GET  /api/history
POST /api/feedback
```

## Response Schema

กำหนด Structure กลาง

## User Schema

กำหนด User Profile Format

## Skill Schema

กำหนด Skill Score Format

## Curriculum Schema

กำหนด Course Data Format

หลังจากตกลงแล้วพยายามไม่เปลี่ยน Structure ใหญ่ในช่วง Day 2–5

---

# 19. สิ่งที่ต้องมีใน Demo

## Demo 1 — Login

```text
Google Sign-In
→ Onboarding
→ Main AI
```

## Demo 2 — Department RAG

ถาม

> ภาควิชาวิศวกรรมคอมพิวเตอร์เรียนเกี่ยวกับอะไร

AI ใช้ Department RAG และแสดง Source

## Demo 3 — Curriculum

ถาม

> ปี 2 เทอม 1 เรียนอะไรบ้าง

Agent เลือก Curriculum Tool

ระบบแสดง **Table UI**

## Demo 4 — Skill Agent Flow

ถาม

> ช่วยวิเคราะห์ Skill ของผม

หากยังไม่มี Skill Profile

```text
Agent
→ Request Assessment
→ User Answers
→ Calculate
→ Save Profile
→ Radar Chart
```

## Demo 5 — History

เปิดประวัติ Conversation ที่เคยถาม

## Demo 6 — Feedback

กด 👍 / 👎 ต่อคำตอบ AI

---

# 20. Definition of Done

Mini Project ถือว่าเสร็จเมื่อสามารถทำสิ่งต่อไปนี้ได้

- [ ] Google Login ใช้งานได้
- [ ] New User ทำ Onboarding ได้
- [ ] User Profile ถูกเก็บ
- [ ] Main 3D AI Mascot **COPIE** **COPIE** **COPIE** แสดงผลได้
- [ ] User สามารถส่งคำถามได้
- [ ] Agent สามารถแยก Intent ได้
- [ ] Agent สามารถเรียก Department RAG ได้
- [ ] Agent สามารถเรียก Curriculum Tool ได้
- [ ] Agent สามารถเรียก Skill Assessment ได้
- [ ] Agent สามารถตรวจว่าข้อมูล Skill ยังไม่มีได้
- [ ] Assessment Form แสดงผ่าน Dynamic UI ได้
- [ ] Skill Result แสดง Radar Chart ได้
- [ ] Curriculum แสดงเป็น Table ได้
- [ ] RAG แสดง Source ได้
- [ ] Conversation History ถูกเก็บ
- [ ] Feedback ถูกเก็บ
- [ ] ระบบสามารถ Demo แบบ End-to-End ได้

Optional

- [ ] Suggested Questions
- [ ] Copy Response
- [ ] Export Conversation

---

# 21. Technology Suggestion

## Frontend

- Next.js
- TypeScript
- Tailwind CSS
- React Three Fiber
- Drei
- Framer Motion
- Recharts

## Backend

- FastAPI หรือ Node.js ตามความถนัดของทีม

## Authentication

- Google OAuth

## AI

- LLM API ที่ทีมเลือกใช้
- Structured Output / Tool Calling

## RAG

- Embedding Model
- FAISS หรือ Chroma

## Database

สำหรับ Mini Project สามารถใช้

- PostgreSQL
- MongoDB
- Supabase

หรือฐานข้อมูลที่ทีมมีประสบการณ์อยู่แล้ว

---

# 22. Scope Control

เนื่องจากระยะเวลาพัฒนาเพียง 5 วัน ควรหลีกเลี่ยง

- Career Recommendation ขนาดใหญ่
- Learning Roadmap แบบซับซ้อน
- ระบบ Admin เต็มรูปแบบ
- Real-time Voice Assistant
- Multi-agent architecture ที่ซับซ้อน
- 3D Environment ขนาดใหญ่
- Animation Mascot จำนวนมาก
- Feature ที่ไม่มีผลกับ Core Demo

ควรเน้น

**Agent Intelligence + Department Knowledge + Dynamic Visualization + 3D User Experience**

---

# 23. Project Summary

**RMUTT Computer Engineering AI Assistant** คือระบบ AI Assistant สำหรับ **ภาควิชาวิศวกรรมคอมพิวเตอร์ มหาวิทยาลัยเทคโนโลยีราชมงคลธัญบุรี**

ระบบใช้ AI Agent เพื่อเข้าใจคำถามของผู้ใช้ เลือก Tool ที่เหมาะสม และนำเสนอคำตอบในรูปแบบที่เหมาะกับข้อมูล ไม่จำกัดเฉพาะข้อความ

จุดเด่นหลักของระบบคือ

```text
3D AI Mascot **COPIE** **COPIE**
      +
AI Agent
      +
Department-Specific RAG
      +
Curriculum Structured Data
      +
Skill Assessment
      +
Dynamic UI
      +
User Context / History / Feedback
```

โดยออกแบบ Scope ให้ทีม Core จำนวน 6 คนสามารถพัฒนาระบบหลักได้ภายใน 5 วัน และให้สมาชิกอีก 2 คนรับผิดชอบ Optional Feature ที่มีขนาดเล็กและไม่เป็น Dependency ของระบบหลัก
