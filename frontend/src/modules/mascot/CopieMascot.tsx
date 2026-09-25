import Image from "next/image";

import { COPIE_IMAGE_SIZE, COPIE_IMAGES, type CopieMascotState } from "./states";

type Layout = "center" | "rail" | "hidden";

type CopieMascotProps = {
  state?: CopieMascotState;
  layout?: Layout;
  priority?: boolean;
  className?: string;
};

// Renders inside a `.copie-ui` container so the kit's .copie-mascot sizing and motion apply.
export function CopieMascot({ state = "idle", layout = "center", priority, className = "" }: CopieMascotProps) {
  return (
    <Image
      src={COPIE_IMAGES[state]}
      alt={`COPIE (${state})`}
      width={COPIE_IMAGE_SIZE.width}
      height={COPIE_IMAGE_SIZE.height}
      priority={priority}
      data-layout={layout === "center" ? undefined : layout}
      className={`copie-mascot copie-mascot-breathe ${className}`}
    />
  );
}
