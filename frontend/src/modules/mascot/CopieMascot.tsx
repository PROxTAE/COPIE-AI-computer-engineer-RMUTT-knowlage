"use client";

import { useState } from "react";
import Image from "next/image";

import { useMascotMode } from "./modeContext";
import {
  COPIE_IMAGE_SIZE,
  COPIE_STATES,
  copieImage,
  type CopieMascotState,
  type InteractionMode,
} from "./states";

type Layout = "center" | "rail" | "hidden";

type CopieMascotProps = {
  state?: CopieMascotState;
  /** Defaults to the mode from <MascotModeProvider>, else "normal". */
  mode?: InteractionMode;
  layout?: Layout;
  priority?: boolean;
  animated?: boolean;
  className?: string;
};

// The eight state images of the current mode load eagerly and stay mounted so CSS
// can crossfade between them without a blank frame. When the mode changes, the old
// mode keeps showing until the new mode's image for the current state has loaded,
// then both sets crossfade; the old set unmounts afterwards. Only one mode's set is
// loaded at rest, so the page never fetches all 24 images at once.
export function CopieMascot({
  state = "idle",
  mode: modeProp,
  layout = "center",
  priority,
  animated = true,
  className = "",
}: CopieMascotProps) {
  const contextMode = useMascotMode();
  const mode = modeProp ?? contextMode;
  const [loaded, setLoaded] = useState<ReadonlySet<string>>(() => new Set());
  const [shownMode, setShownMode] = useState(mode);
  const sizes = layout === "rail" ? "(max-width: 900px) 34vw, 20vw" : "(max-width: 900px) 82vw, 48vw";
  const dataLayout = layout === "center" ? undefined : layout;

  const targetReady = loaded.has(copieImage(mode, state));
  if (targetReady && shownMode !== mode) setShownMode(mode);
  const visibleMode = targetReady ? mode : shownMode;
  const layerModes = visibleMode === mode ? [mode] : [visibleMode, mode];

  if (!animated) {
    return (
      <Image
        src={copieImage(mode, state)}
        alt={`COPIE (${state})`}
        width={COPIE_IMAGE_SIZE.width}
        height={COPIE_IMAGE_SIZE.height}
        sizes={sizes}
        preload={priority}
        data-layout={dataLayout}
        className={`copie-mascot copie-mascot-breathe ${className}`}
      />
    );
  }

  const markLoaded = (src: string) =>
    setLoaded((current) => (current.has(src) ? current : new Set(current).add(src)));

  return (
    <span className="relative inline-grid place-items-center" data-copie-state={state} data-mascot-mode={visibleMode}>
      {layerModes.flatMap((layerMode) =>
        COPIE_STATES.map((imageState) => {
          const src = copieImage(layerMode, imageState);
          const active = layerMode === visibleMode && imageState === state;
          return (
            <Image
              key={src}
              src={src}
              alt={active ? `COPIE (${state})` : ""}
              aria-hidden={active ? undefined : true}
              width={COPIE_IMAGE_SIZE.width}
              height={COPIE_IMAGE_SIZE.height}
              sizes={sizes}
              loading="eager"
              preload={Boolean(priority && layerMode === mode && imageState === state)}
              onLoad={() => markLoaded(src)}
              data-layout={dataLayout}
              data-active={active}
              className={`copie-mascot copie-mascot-layer copie-mascot-breathe col-start-1 row-start-1 ${className}`}
            />
          );
        }),
      )}
    </span>
  );
}
