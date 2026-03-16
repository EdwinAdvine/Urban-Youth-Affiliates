type BadgeVariant =
  | "pending"
  | "approved"
  | "rejected"
  | "paid"
  | "suspended"
  | "processing"
  | "failed"
  | "active"
  | "inactive"
  | "info";

const variantClasses: Record<BadgeVariant, string> = {
  pending: "badge-pending",
  approved: "badge-approved",
  rejected: "badge-rejected",
  paid: "badge-paid",
  suspended: "bg-orange-100 text-orange-700",
  processing: "bg-blue-100 text-blue-700",
  failed: "badge-rejected",
  active: "badge-approved",
  inactive: "bg-gray-100 text-gray-600",
  info: "bg-gray-100 text-gray-700",
};

interface BadgeProps {
  variant?: BadgeVariant;
  /** Auto-detect variant from string value */
  value?: string;
  children: React.ReactNode;
  className?: string;
}

function detectVariant(value: string): BadgeVariant {
  const v = value.toLowerCase() as BadgeVariant;
  return v in variantClasses ? v : "info";
}

export function Badge({ variant, value, children, className = "" }: BadgeProps) {
  const resolved = variant ?? (value ? detectVariant(value) : "info");
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variantClasses[resolved]} ${className}`}>
      {children}
    </span>
  );
}

/** Convenience: renders status string as a Badge automatically. */
export function StatusBadge({ status }: { status: string }) {
  return (
    <Badge value={status}>
      {status.charAt(0).toUpperCase() + status.slice(1)}
    </Badge>
  );
}
