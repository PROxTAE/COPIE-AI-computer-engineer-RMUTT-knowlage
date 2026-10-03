"use client";

import { Button, Popover } from "@heroui/react";
import { User as UserIcon, LogOut } from "lucide-react";
import { useRouter } from "next/navigation";

import { useChatStore } from "@/modules/core";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";

export function ProfileControl({ user }: { user: User }) {
  const router = useRouter();
  const name = user.display_name ?? user.name;

  const logout = () => {
    useChatStore.getState().newConversation();
    useUserStore.getState().clearSession();
    router.replace("/login");
  };

  return (
    <Popover>
      <Popover.Trigger className="flex size-10 items-center justify-center rounded-full border-2 border-[#155ff2] bg-white text-[#155ff2] hover:bg-blue-50 transition-all shadow-xs cursor-pointer">
        <UserIcon className="size-5" />
      </Popover.Trigger>
      <Popover.Content
        aria-label="โปรไฟล์ผู้ใช้"
        placement="bottom end"
        className="w-60 rounded-2xl border border-[#d2e0f5] bg-white p-4 shadow-xl"
      >
        <div className="flex items-center gap-3 pb-3 border-b border-[#d2e0f5]/60">
          <div className="flex size-10 items-center justify-center rounded-full bg-blue-50 text-[#155ff2] font-display font-bold">
            {name.charAt(0).toUpperCase()}
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate font-display text-sm font-bold text-[#080b12]">{name}</p>
            <p className="truncate text-xs text-[#6b82a6]">{user.email}</p>
          </div>
        </div>

        <Button
          className="mt-3 w-full flex items-center justify-center gap-2 rounded-xl border border-red-200 bg-red-50 text-red-600 hover:bg-red-100 font-medium text-xs py-2"
          variant="outline"
          onPress={logout}
        >
          <LogOut className="size-3.5" />
          <span>ออกจากระบบ</span>
        </Button>
      </Popover.Content>
    </Popover>
  );
}
