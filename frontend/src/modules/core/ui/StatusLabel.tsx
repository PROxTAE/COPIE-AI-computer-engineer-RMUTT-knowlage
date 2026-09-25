type StatusLabelProps = {
  label?: string;
  active?: boolean;
  className?: string;
};

export function StatusLabel({ label = "AI // ACTIVE", active = true, className = "" }: StatusLabelProps) {
  return (
    <span className={`copie-status inline-flex items-center gap-2 ${className}`}>
      {active && <span className="copie-status-dot copie-status-pulse" aria-hidden="true" />}
      {label}
    </span>
  );
}
