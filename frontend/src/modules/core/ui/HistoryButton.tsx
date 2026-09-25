"use client";

import { Button } from "@heroui/react";

import { Icon } from "./Icon";

type HistoryButtonProps = {
  onPress?: () => void;
  isDisabled?: boolean;
};

export function HistoryButton({ onPress, isDisabled = false }: HistoryButtonProps) {
  return (
    <Button variant="outline" onPress={onPress} isDisabled={isDisabled || !onPress} className="gap-2 rounded-full bg-white px-5">
      <Icon name="history" size={19} />
      History
    </Button>
  );
}
