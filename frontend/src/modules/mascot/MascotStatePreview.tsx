"use client";

import { useState } from "react";
import { Button } from "@heroui/react";

import { CopieMascot } from "./CopieMascot";
import { COPIE_IMAGES, type CopieMascotState } from "./states";

const STATES = Object.keys(COPIE_IMAGES) as CopieMascotState[];

export function MascotStatePreview() {
  const [state, setState] = useState<CopieMascotState>("idle");

  return (
    <section className="copie-panel flex flex-col items-center gap-5 p-5" aria-label="ตรวจการเปลี่ยนสถานะของมาสคอต">
      <span className="copie-status">COPIE / {state}</span>
      <CopieMascot state={state} className="max-h-80 w-auto!" />
      <div className="flex flex-wrap justify-center gap-2">
        {STATES.map((option) => (
          <Button key={option} variant={option === state ? "primary" : "outline"} onPress={() => setState(option)}>
            {option}
          </Button>
        ))}
      </div>
    </section>
  );
}
