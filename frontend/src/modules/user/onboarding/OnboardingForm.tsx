"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@heroui/react";
import { useRouter } from "next/navigation";

import { ApiError } from "@/modules/core";
import type { AgeRange, ProfileUpdate, User, UserType } from "@/types/contract";

import { useUserStore } from "../userStore";

const AGE_OPTIONS: { value: AgeRange; label: string }[] = [
  { value: "under_18", label: "ต่ำกว่า 18 ปี" },
  { value: "18_20", label: "18–20 ปี" },
  { value: "21_23", label: "21–23 ปี" },
  { value: "24_plus", label: "24 ปีขึ้นไป" },
];

const USER_TYPE_OPTIONS: { value: UserType; label: string }[] = [
  { value: "prospective", label: "ผู้สนใจเข้าศึกษา" },
  { value: "current_student", label: "นักศึกษาปัจจุบัน" },
  { value: "near_graduate", label: "ใกล้สำเร็จการศึกษา" },
];

type OnboardingFormProps = { user: User };

function Choice({
  checked,
  label,
  name,
  value,
  onChange,
}: {
  checked: boolean;
  label: string;
  name: string;
  value: string;
  onChange: () => void;
}) {
  return (
    <label className={`cursor-pointer rounded-xl border px-4 py-3 text-center text-sm font-semibold transition focus-within:ring-2 focus-within:ring-cyber-blue focus-within:ring-offset-2 ${
      checked
        ? "border-cyber-blue bg-blue-50 text-cyber-blue ring-1 ring-cyber-blue"
        : "border-cyber-line bg-white text-cyber-muted hover:border-blue-300"
    }`}>
      <input
        className="sr-only"
        type="radio"
        name={name}
        value={value}
        checked={checked}
        onChange={onChange}
      />
      {label}
    </label>
  );
}

export function OnboardingForm({ user }: OnboardingFormProps) {
  const router = useRouter();
  const updateProfile = useUserStore((state) => state.updateProfile);
  const [displayName, setDisplayName] = useState(user.display_name ?? user.name);
  const [ageRange, setAgeRange] = useState<AgeRange | "">(user.age_range ?? "");
  const [userType, setUserType] = useState<UserType | "">(user.user_type ?? "");
  const [studyYear, setStudyYear] = useState<number | null>(user.study_year);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const needsStudyYear = userType === "current_student" || userType === "near_graduate";

  const selectUserType = (value: UserType) => {
    setUserType(value);
    if (value === "prospective") setStudyYear(null);
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (pending) return;

    const normalizedName = displayName.trim();
    if (!normalizedName || normalizedName.length > 50) {
      setError("ชื่อที่อยากให้เรียกต้องมีความยาว 1–50 ตัวอักษร");
      return;
    }
    if (!ageRange || !userType) {
      setError("กรุณาเลือกช่วงอายุและสถานะผู้ใช้งาน");
      return;
    }
    if (needsStudyYear && studyYear === null) {
      setError("กรุณาเลือกชั้นปี");
      return;
    }

    const profile: ProfileUpdate = {
      display_name: normalizedName,
      age_range: ageRange,
      user_type: userType,
      study_year: needsStudyYear ? studyYear : null,
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
    <form className="grid gap-5" onSubmit={(event) => { void submit(event); }} noValidate>
      <label className="grid gap-2 font-semibold text-cyber-ink">
        ชื่อที่อยากให้เรียก
        <input
          className="rounded-xl border border-cyber-line bg-white px-4 py-3 font-normal outline-none focus:border-cyber-blue focus:ring-2 focus:ring-blue-100"
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          autoComplete="nickname"
          minLength={1}
          maxLength={50}
          disabled={pending}
          required
        />
      </label>

      <fieldset className="grid gap-3" disabled={pending}>
        <legend className="mb-2 font-semibold text-cyber-ink">ช่วงอายุ</legend>
        <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
          {AGE_OPTIONS.map((option) => (
            <Choice
              key={option.value}
              checked={ageRange === option.value}
              label={option.label}
              name="age_range"
              value={option.value}
              onChange={() => setAgeRange(option.value)}
            />
          ))}
        </div>
      </fieldset>

      <fieldset className="grid gap-3" disabled={pending}>
        <legend className="mb-2 font-semibold text-cyber-ink">สถานะผู้ใช้งาน</legend>
        <div className="grid gap-2 sm:grid-cols-3">
          {USER_TYPE_OPTIONS.map((option) => (
            <Choice
              key={option.value}
              checked={userType === option.value}
              label={option.label}
              name="user_type"
              value={option.value}
              onChange={() => selectUserType(option.value)}
            />
          ))}
        </div>
      </fieldset>

      {needsStudyYear && (
        <fieldset className="grid gap-3" disabled={pending}>
          <legend className="mb-2 font-semibold text-cyber-ink">ชั้นปี</legend>
          <div className="grid grid-cols-4 gap-2">
            {[1, 2, 3, 4].map((year) => (
              <Choice
                key={year}
                checked={studyYear === year}
                label={`ปี ${year}`}
                name="study_year"
                value={String(year)}
                onChange={() => setStudyYear(year)}
              />
            ))}
          </div>
        </fieldset>
      )}

      {error && <p className="text-sm text-red-700" role="alert">{error}</p>}
      <Button type="submit" size="lg" variant="primary" isDisabled={pending} className="mt-1 w-full">
        {pending ? "กำลังบันทึก..." : "เริ่มใช้งาน COPIE"}
      </Button>
    </form>
  );
}
