"use client";

import { Button, Popover } from "@heroui/react";
import { useRouter } from "next/navigation";

import { useChatStore } from "@/modules/core";
import type { User } from "@/types/contract";

import { useUserStore } from "../userStore";

export function ProfileControl({ user }: { user: User }) {
  const router = useRouter();
  const name = user.display_name ?? user.name;
  const initial = name.trim().charAt(0).toUpperCase() || "U";

  const logout = () => {
    useChatStore.getState().newConversation();
    useUserStore.getState().clearSession();
    router.replace("/login");
  };

  return (
    <Popover>
      <Popover.Trigger className="flex items-center gap-2 rounded-full border border-cyber-line bg-white px-2 py-1.5 text-sm font-semibold text-cyber-ink">
        <span className="grid size-8 place-items-center rounded-full bg-cyber-blue text-white" aria-hidden="true">{initial}</span>
        <span className="hidden max-w-36 truncate sm:block">{name}</span>
      </Popover.Trigger>
      <Popover.Content
        aria-label="โปรไฟล์ผู้ใช้"
        placement="bottom end"
        className="w-56 rounded-2xl border border-cyber-line bg-white p-3 shadow-xl"
      >
        <p className="truncate text-sm font-semibold text-cyber-ink">{name}</p>
        <p className="truncate text-xs text-cyber-muted">{user.email}</p>
        <Button className="mt-3 w-full" variant="outline" onPress={logout}>ออกจากระบบ</Button>
      </Popover.Content>
    </Popover>
  );
}
