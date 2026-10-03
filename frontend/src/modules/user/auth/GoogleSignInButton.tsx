"use client";

import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { GoogleLogin, GoogleOAuthProvider, type CredentialResponse } from "@react-oauth/google";

import { ApiError } from "@/modules/core";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";

type GoogleSignInButtonProps = {
  disabled?: boolean;
  onAuthenticated: (user: User) => void;
  onOpenDevLogin?: () => void;
};

export function GoogleSignInButton({ disabled = false, onAuthenticated, onOpenDevLogin }: GoogleSignInButtonProps) {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.trim() ?? "";
  const loginWithGoogle = useUserStore((state) => state.loginWithGoogle);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSuccess = async (response: CredentialResponse) => {
    if (!response.credential) {
      setError("Google ไม่ได้ส่งข้อมูลยืนยันตัวตน กรุณาลองใหม่");
      return;
    }
    setPending(true);
    setError(null);
    try {
      const user = await loginWithGoogle(response.credential);
      onAuthenticated(user);
    } catch (caught) {
      setError(caught instanceof ApiError
        ? caught.message
        : "เข้าสู่ระบบด้วย Google ไม่สำเร็จ กรุณาลองใหม่");
    } finally {
      setPending(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-2">
      <div className={`relative inline-block ${disabled || pending ? "pointer-events-none opacity-60" : ""}`}>
        {/* Mockup 01-login-v2 Pill Button Design */}
        <div className="group relative flex items-center gap-4 rounded-full border-2 border-[#155ff2] bg-white px-7 py-3.5 shadow-[0_8px_24px_rgba(21,95,242,0.12)] hover:shadow-[0_12px_28px_rgba(21,95,242,0.2)] hover:-translate-y-0.5 transition-all cursor-pointer">
          {/* Google Multi-colored SVG Icon */}
          <svg className="size-6 shrink-0" viewBox="0 0 24 24">
            <path
              fill="#4285F4"
              d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.05h3.88c2.27-2.09 3.665-5.17 3.665-9.15z"
            />
            <path
              fill="#34A853"
              d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.88-3.05c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.27v3.15C3.26 21.36 7.33 24 12 24z"
            />
            <path
              fill="#FBBC05"
              d="M5.28 14.27c-.25-.72-.38-1.49-.38-2.27s.13-1.55.38-2.27V6.58H1.27C.46 8.2 0 10.04 0 12s.46 3.8 1.27 5.42l4.01-3.15z"
            />
            <path
              fill="#EA4335"
              d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.33 0 3.26 2.64 1.27 6.58l4.01 3.15c.95-2.83 3.6-4.98 6.72-4.98z"
            />
          </svg>

          {/* Vertical Separator */}
          <span className="h-6 w-px bg-[#d2e0f5]" />

          {/* Label */}
          <span className="font-display font-semibold text-base text-[#080b12]">
            เข้าสู่ระบบด้วย Google
          </span>

          {/* Right Arrow */}
          <ArrowRight className="size-5 text-[#155ff2] ml-2 group-hover:translate-x-1 transition-transform" />

          {/* Overlay Google OAuth Login element if clientId is configured */}
          {clientId ? (
            <div className="absolute inset-0 opacity-0 overflow-hidden rounded-full cursor-pointer">
              <GoogleOAuthProvider clientId={clientId}>
                <GoogleLogin
                  onSuccess={(response) => { void handleSuccess(response); }}
                  onError={() => setError("เข้าสู่ระบบด้วย Google ไม่สำเร็จ กรุณาลองใหม่")}
                  text="continue_with"
                  shape="pill"
                  size="large"
                  width="360"
                />
              </GoogleOAuthProvider>
            </div>
          ) : (
            <button
              type="button"
              onClick={onOpenDevLogin}
              className="absolute inset-0 opacity-0 rounded-full cursor-pointer"
              aria-label="เข้าสู่ระบบ"
            />
          )}
        </div>
      </div>

      {pending && <p className="text-sm text-cyber-blue font-medium" role="status">กำลังเข้าสู่ระบบ...</p>}
      {error && <p className="text-sm text-red-700 font-medium" role="alert">{error}</p>}
    </div>
  );
}
