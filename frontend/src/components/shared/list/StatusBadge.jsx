import { Check, X } from "lucide-react";

export function StatusBadge({ status }) {
  const isMatch = status === "match";
  return (
    <div
      className={`status-circle ${isMatch ? "status-match" : "status-mismatch"}`}
    >
      {isMatch ? (
        <Check size={26} strokeWidth={4} />
      ) : (
        <X size={26} strokeWidth={4} />
      )}
    </div>
  );
}
