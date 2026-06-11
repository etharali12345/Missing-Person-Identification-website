import { Check, X, AlertTriangle } from "lucide-react";

export function StatusBadge({ status }) {
  const config = {
    match: { className: "status-match", Icon: Check, size: 26, strokeWidth: 4 },
    uncertain: {
      className: "status-uncertain",
      Icon: AlertTriangle,
      size: 24,
      strokeWidth: 3,
    },
    nomatch: {
      className: "status-mismatch",
      Icon: X,
      size: 26,
      strokeWidth: 4,
    },
  };

  const { className, Icon, size, strokeWidth } =
    config[status] ?? config.nomatch;

  return (
    <div className={`status-circle ${className}`}>
      <Icon size={size} strokeWidth={strokeWidth} />
    </div>
  );
}
