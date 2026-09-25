import Image from "next/image";

import { COPIE_IMAGE_SIZE, COPIE_IMAGES, type CopieMascotState } from "./states";

type Layout = "center" | "rail" | "hidden";

type CopieMascotProps = {
  state?: CopieMascotState;
  layout?: Layout;
  priority?: boolean;
  animated?: boolean;
  className?: string;
};

// All eight small state images load eagerly on entry to the page. Keeping the
// layers mounted lets CSS crossfade between them without a blank frame.
export function CopieMascot({ state = "idle", layout = "center", priority, animated = true, className = "" }: CopieMascotProps) {
  const sizes = layout === "rail" ? "(max-width: 900px) 34vw, 20vw" : "(max-width: 900px) 82vw, 48vw";
  if (!animated) {
    return (
      <Image
        src={COPIE_IMAGES[state]}
        alt={`COPIE (${state})`}
        width={COPIE_IMAGE_SIZE.width}
        height={COPIE_IMAGE_SIZE.height}
        sizes={sizes}
        preload={priority}
        data-layout={layout === "center" ? undefined : layout}
        className={`copie-mascot copie-mascot-breathe ${className}`}
      />
    );
  }

  return (
    <span className="relative inline-grid place-items-center" data-copie-state={state}>
      {(Object.keys(COPIE_IMAGES) as CopieMascotState[]).map((imageState) => (
        <Image
          key={imageState}
          src={COPIE_IMAGES[imageState]}
          alt={imageState === state ? `COPIE (${state})` : ""}
          aria-hidden={imageState === state ? undefined : true}
          width={COPIE_IMAGE_SIZE.width}
          height={COPIE_IMAGE_SIZE.height}
          sizes={sizes}
          loading="eager"
          preload={Boolean(priority && imageState === state)}
          data-layout={layout === "center" ? undefined : layout}
          data-active={imageState === state}
          className={`copie-mascot copie-mascot-layer copie-mascot-breathe col-start-1 row-start-1 ${className}`}
        />
      ))}
    </span>
  );
}
