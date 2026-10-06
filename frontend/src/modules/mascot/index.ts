// Public API of the "mascot" module (P1).
// Other modules import only from "@/modules/mascot".
export { CopieMascot } from "./CopieMascot"; // 2.5D image stack (transparent images per state and mode)
export { MascotStage } from "./MascotStage"; // interactive stage: parallax, tilt, squash, bubbles
export { MascotModeProvider, useMascotMode } from "./modeContext";
export { MascotStatePreview } from "./MascotStatePreview"; // theme preview only
export {
  COPIE_IMAGES,
  COPIE_STATES,
  INTERACTION_MODES,
  copieImage,
  type CopieMascotState,
  type InteractionMode,
} from "./states";
export { DOCK_GUARD, MascotDock, type DockCorner } from "./MascotDock"; // mini COPIE in a screen corner while the mascot is hidden
