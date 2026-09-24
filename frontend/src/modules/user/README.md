# user — Auth / Onboarding / History / Feedback (frontend)

| | |
|---|---|
| เจ้าของ | **P2** |
| แผนงาน | [`02_USER_SYSTEM.md`](../../../../IMPLEMENTATION_PLANS/02_USER_SYSTEM.md) |
| Branch prefix | ดู `IMPLEMENTATION_PLANS/00_GIT_DELIVERY_RULES.md` §2 |

## หน้าที่

Google Sign-In + Dev Login, เก็บ token, `AuthGuard`, ฟอร์ม Onboarding, History sidebar และปุ่ม 👍/👎 — คู่กับ `backend/app/modules/user`

## โครงไฟล์ที่จะสร้าง

```text
user/
├─ index.ts
├─ auth/          # GoogleSignInButton, DevLoginButton, AuthGuard, token.ts, LoginPage
├─ onboarding/    # OnboardingForm, OnboardingPage
├─ history/       # HistorySidebar, ConversationItem
├─ feedback/      # FeedbackBar, ReasonDialog
└─ userStore.ts
```

## Public API (สิ่งที่ module อื่นเรียกใช้ได้)

`LoginPage`, `OnboardingPage`, `AuthGuard`, `HistorySidebar`, `FeedbackBar`, `useUserStore`, `getToken`, `clearToken`

## ใช้ของ module อื่นได้จาก

`@/modules/core` (ui, api, useChatStore.loadConversation), `@/types/contract`
