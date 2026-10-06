import type { CSSProperties } from "react";

export const ICON_NAMES = [
  "arrow-left", "book-open", "calendar", "chart-bars", "chevron-right",
  "close", "copy", "document", "eye-off", "filter", "graduation-cap",
  "history", "info", "menu", "mode-developer", "mode-devil", "profile", "refresh", "search", "send",
  "spark", "thumb-down", "thumb-up",
] as const;

export type IconName = (typeof ICON_NAMES)[number];

type IconProps = {
  name: IconName;
  size?: number;
  label?: string;
  className?: string;
};

export function Icon({ name, size = 20, label, className = "" }: IconProps) {
  const url = `url("/copie-ui/icons/${name}.svg")`;
  const style: CSSProperties = {
    width: size,
    height: size,
    backgroundColor: "currentColor",
    maskImage: url,
    WebkitMaskImage: url,
    maskPosition: "center",
    WebkitMaskPosition: "center",
    maskRepeat: "no-repeat",
    WebkitMaskRepeat: "no-repeat",
    maskSize: "contain",
    WebkitMaskSize: "contain",
  };

  return (
    <span
      className={`inline-block shrink-0 ${className}`}
      style={style}
      role={label ? "img" : undefined}
      aria-label={label}
      aria-hidden={label ? undefined : true}
    />
  );
}
