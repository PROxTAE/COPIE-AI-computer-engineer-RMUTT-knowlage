"use client";

import { useState, type FormEvent } from "react";
import { ArrowRight, Calendar, GraduationCap, BarChart2, User as UserIcon, X } from "lucide-react";
import { useRouter } from "next/navigation";

import { ApiError } from "@/modules/core";
import type { AgeRange, ProfileUpdate, User, UserType } from "@/types/contract";

import { useUserStore } from "../userStore";

const AGE_OPTIONS: { value: AgeRange; label: string }[] = [
  { value: "under_18", label: "ต่ำกว่า 18 ปี" },
  { value: "18_20", label: "18 – 20 ปี" },
  { value: "21_23", label: "21 – 23 ปี" },
  { value: "24_plus", label: "24 ปีขึ้นไป" },
];

const USER_TYPE_OPTIONS: { value: UserType | "other"; label: string }[] = [
  { value: "current_student", label: "นักศึกษาปัจจุบัน" },
  { value: "near_graduate", label: "จบการศึกษาแล้ว" },
  { value: "prospective", label: "บุคคลทั่วไป" },
  { value: "other", label: "อื่น ๆ" },
];

const YEAR_OPTIONS = [
  { value: 1, label: "ปี 1" },
  { value: 2, label: "ปี 2" },
  { value: 3, label: "ปี 3" },
  { value: 4, label: "ปี 4" },
  { value: 5, label: "อื่น ๆ" },
];

type OnboardingFormProps = { user: User };

export function OnboardingForm({ user }: OnboardingFormProps) {
  const router = useRouter();
  const updateProfile = useUserStore((state) => state.updateProfile);
  const [displayName, setDisplayName] = useState(user.display_name ?? user.name ?? "Tae");
  const [ageRange, setAgeRange] = useState<AgeRange>("21_23");
  const [userType, setUserType] = useState<UserType | "other">("current_student");
  const [studyYear, setStudyYear] = useState<number>(3);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (pending) return;

    const normalizedName = displayName.trim();
    if (!normalizedName || normalizedName.length > 50) {
      setError("ชื่อที่อยากให้เรียกต้องมีความยาว 1–50 ตัวอักษร");
      return;
    }

    const mappedUserType: UserType = userType === "other" ? "prospective" : userType;
    const isStudent = mappedUserType === "current_student" || mappedUserType === "near_graduate";

    const profile: ProfileUpdate = {
      display_name: normalizedName,
      age_range: ageRange,
      user_type: mappedUserType,
      study_year: isStudent ? Math.min(studyYear, 4) : null,
    };

    setPending(true);
    setError(null);
    try {
      const updatedUser = await updateProfile(profile);
      if (!updatedUser.onboarded) {
        setError("บันทึกข้อมูลแล้วแต่สถานะเริ่มใช้งานยังไม่สมบูรณ์ กรุณาลองใหม่");
        return;
      }
      router.replace("/chat");
    } catch (caught) {
      setError(caught instanceof ApiError
        ? caught.message
        : "บันทึกข้อมูลไม่สำเร็จ กรุณาลองใหม่");
    } finally {
      setPending(false);
    }
  };

  return (
    <form className="grid gap-6" onSubmit={(event) => { void submit(event); }} noValidate>
      {/* Field 1: Name */}
      <div className="grid grid-cols-1 sm:grid-cols-[160px_1fr] items-center gap-3">
        <label className="flex items-center gap-2.5 font-display text-sm font-bold text-[#080b12]">
          <UserIcon className="size-4.5 text-[#155ff2] shrink-0" />
          ชื่อที่อยากให้เรียก
        </label>
        <div className="relative flex items-center">
          <input
            className="w-full rounded-xl border border-[#a9bee0] bg-white px-4 py-3 pr-10 font-sans text-base text-[#080b12] outline-none focus:border-[#155ff2] focus:ring-2 focus:ring-[#155ff2]/20 transition-all shadow-xs"
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            autoComplete="nickname"
            minLength={1}
            maxLength={50}
            disabled={pending}
            placeholder="ใส่ชื่อที่ต้องการให้ COPIE เรียก"
            required
          />
          {displayName.length > 0 && (
            <button
              type="button"
              onClick={() => setDisplayName("")}
              className="absolute right-3 text-[#6b82a6] hover:text-[#080b12] p-1 cursor-pointer"
              aria-label="ลบชื่อ"
            >
              <X className="size-4" />
            </button>
          )}
        </div>
      </div>

      {/* Field 2: Age Range */}
      <div className="grid grid-cols-1 sm:grid-cols-[160px_1fr] items-center gap-3">
        <span className="flex items-center gap-2.5 font-display text-sm font-bold text-[#080b12]">
          <Calendar className="size-4.5 text-[#155ff2] shrink-0" />
          ช่วงอายุ
        </span>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {AGE_OPTIONS.map((option) => {
            const isSelected = ageRange === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setAgeRange(option.value)}
                disabled={pending}
                className={`rounded-xl px-3 py-3 text-center text-sm font-semibold transition-all cursor-pointer shadow-xs ${
                  isSelected
                    ? "border-2 border-[#155ff2] bg-white text-[#155ff2] shadow-[0_0_12px_rgba(21,95,242,0.15)]"
                    : "border border-[#d2e0f5] bg-white text-[#6b82a6] hover:border-[#155ff2]/50 hover:bg-slate-50"
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Field 3: User Status */}
      <div className="grid grid-cols-1 sm:grid-cols-[160px_1fr] items-center gap-3">
        <span className="flex items-center gap-2.5 font-display text-sm font-bold text-[#080b12]">
          <GraduationCap className="size-4.5 text-[#155ff2] shrink-0" />
          สถานะผู้ใช้งาน
        </span>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {USER_TYPE_OPTIONS.map((option) => {
            const isSelected = userType === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setUserType(option.value)}
                disabled={pending}
                className={`rounded-xl px-3 py-3 text-center text-sm font-semibold transition-all cursor-pointer shadow-xs ${
                  isSelected
                    ? "border-2 border-[#155ff2] bg-[#155ff2] text-white shadow-[0_4px_14px_rgba(21,95,242,0.3)]"
                    : "border border-[#d2e0f5] bg-white text-[#6b82a6] hover:border-[#155ff2]/50 hover:bg-slate-50"
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Field 4: Study Year */}
      <div className="grid grid-cols-1 sm:grid-cols-[160px_1fr] items-center gap-3">
        <span className="flex items-center gap-2.5 font-display text-sm font-bold text-[#080b12]">
          <BarChart2 className="size-4.5 text-[#155ff2] shrink-0" />
          ชั้นปี
        </span>
        <div className="grid grid-cols-5 gap-2">
          {YEAR_OPTIONS.map((option) => {
            const isSelected = studyYear === option.value;
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setStudyYear(option.value)}
                disabled={pending}
                className={`rounded-xl px-2 py-3 text-center text-sm font-semibold transition-all cursor-pointer shadow-xs ${
                  isSelected
                    ? "border-2 border-[#155ff2] bg-white text-[#155ff2] shadow-[0_0_12px_rgba(21,95,242,0.15)]"
                    : "border border-[#d2e0f5] bg-white text-[#6b82a6] hover:border-[#155ff2]/50 hover:bg-slate-50"
                }`}
              >
                {option.label}
              </button>
            );
          })}
        </div>
      </div>

      {error && <p className="text-sm text-red-700 font-medium" role="alert">{error}</p>}

      {/* Primary CTA Submit Button */}
      <div className="pt-2">
        <button
          type="submit"
          disabled={pending}
          className="group relative flex w-full items-center justify-center gap-3 rounded-full bg-gradient-to-r from-[#0f5ff0] to-[#155ff2] px-8 py-4 font-display text-base font-bold text-white shadow-[0_8px_24px_rgba(21,95,242,0.3)] hover:shadow-[0_12px_32px_rgba(21,95,242,0.45)] hover:-translate-y-0.5 active:translate-y-0 transition-all cursor-pointer disabled:opacity-50"
        >
          <span>{pending ? "กำลังบันทึกข้อมูล..." : "เริ่มต้นใช้งาน COPIE"}</span>
          <ArrowRight className="size-5 group-hover:translate-x-1 transition-transform" />
        </button>
      </div>
    </form>
  );
}
