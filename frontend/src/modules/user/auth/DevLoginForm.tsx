"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@heroui/react";

import { ApiError } from "@/modules/core";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";

type DevLoginFormProps = {
  disabled?: boolean;
  onAuthenticated: (user: User) => void;
};

export function DevLoginForm({ disabled = false, onAuthenticated }: DevLoginFormProps) {
  const loginWithDev = useUserStore((state) => state.loginWithDev);
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const normalizedEmail = email.trim();
    const normalizedName = name.trim();
    if (!normalizedEmail || !normalizedName || pending || disabled) return;

    setPending(true);
    setError(null);
    try {
      const user = await loginWithDev(normalizedEmail, normalizedName);
      onAuthenticated(user);
    } catch (caught) {
      if (caught instanceof ApiError && caught.status === 404) {
        setError("Dev Login ไม่ได้เปิดใช้งานใน backend นี้");
      } else {
        setError(caught instanceof ApiError
          ? caught.message
          : "Dev Login ไม่สำเร็จ กรุณาลองใหม่");
      }
    } finally {
      setPending(false);
    }
  };

  return (
    <details className="w-full rounded-2xl border border-cyber-line bg-white/80 p-4">
      <summary className="cursor-pointer font-label text-sm font-semibold text-cyber-blue">
        Dev Login สำหรับทีมพัฒนา
      </summary>
      <form className="mt-4 grid gap-3" onSubmit={(event) => { void submit(event); }}>
        <label className="grid gap-1 text-sm font-medium text-cyber-ink">
          ชื่อ
          <input
            className="rounded-xl border border-cyber-line bg-white px-3 py-2 outline-none focus:border-cyber-blue focus:ring-2 focus:ring-blue-100"
            value={name}
            onChange={(event) => setName(event.target.value)}
            autoComplete="name"
            maxLength={100}
            required
          />
        </label>
        <label className="grid gap-1 text-sm font-medium text-cyber-ink">
          Email
          <input
            className="rounded-xl border border-cyber-line bg-white px-3 py-2 outline-none focus:border-cyber-blue focus:ring-2 focus:ring-blue-100"
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            autoComplete="email"
            required
          />
        </label>
        <Button type="submit" variant="outline" isDisabled={disabled || pending || !email.trim() || !name.trim()}>
          {pending ? "กำลังเข้าสู่ระบบ..." : "เข้าสู่ระบบสำหรับพัฒนา"}
        </Button>
        {error && <p className="text-sm text-red-700" role="alert">{error}</p>}
      </form>
    </details>
  );
}
