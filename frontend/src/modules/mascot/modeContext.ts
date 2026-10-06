"use client";

import { createContext, useContext } from "react";

import type { InteractionMode } from "./states";

// The chat page provides its interaction mode here, so every <CopieMascot> inside it
// (including ones drawn by other modules, e.g. the assessment form) uses that mode's images.
const MascotModeContext = createContext<InteractionMode>("normal");

export const MascotModeProvider = MascotModeContext.Provider;

export function useMascotMode(): InteractionMode {
  return useContext(MascotModeContext);
}
