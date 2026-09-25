// Public API of the "mascot" module (P1).
// Other modules import only from "@/modules/mascot".
export { Copie, type CopieProps, type CopieState } from "./Copie"; // 3D (GLB) version
export { CopieMascot } from "./CopieMascot"; // 2.5D version (transparent images per state)
export { COPIE_IMAGES, type CopieMascotState } from "./states";
