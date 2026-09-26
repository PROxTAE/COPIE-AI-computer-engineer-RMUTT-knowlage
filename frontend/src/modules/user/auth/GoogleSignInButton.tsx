"use client";

import { useState } from "react";
import { GoogleLogin, GoogleOAuthProvider, type CredentialResponse } from "@react-oauth/google";

import { ApiError } from "@/modules/core";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";

type GoogleSignInButtonProps = {
  disabled?: boolean;
  onAuthenticated: (user: User) => void;
};

export function GoogleSignInButton({ disabled = false, onAuthenticated }: GoogleSignInButtonProps) {
  const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID?.trim() ?? "";
  const loginWithGoogle = useUserStore((state) => state.loginWithGoogle);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!clientId) {
    return (
      <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700" role="alert">
        ยังไม่ได้ตั้งค่า Google Client ID กรุณาติดต่อผู้ดูแลระบบ
      </p>
    );
  }

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
    <div className="flex flex-col items-center gap-3">
      <div className={disabled || pending ? "pointer-events-none opacity-60" : ""} aria-busy={pending}>
        <GoogleOAuthProvider
          clientId={clientId}
          onScriptLoadError={() => setError("โหลดระบบเข้าสู่ระบบของ Google ไม่สำเร็จ กรุณาลองใหม่")}
        >
          <GoogleLogin
            onSuccess={(response) => { void handleSuccess(response); }}
            onError={() => setError("เข้าสู่ระบบด้วย Google ไม่สำเร็จ กรุณาลองใหม่")}
            text="continue_with"
            shape="pill"
            size="large"
            theme="outline"
            width="300"
          />
        </GoogleOAuthProvider>
      </div>
      {pending && <p className="text-sm text-cyber-blue" role="status">กำลังเข้าสู่ระบบ...</p>}
      {error && <p className="text-sm text-red-700" role="alert">{error}</p>}
    </div>
  );
}
