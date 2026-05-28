import { clsx } from "clsx";

type BadgeVariant = "green" | "yellow" | "red" | "gray" | "blue" | "orange";

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
}

const variantClasses: Record<BadgeVariant, string> = {
  green:  "bg-green-100 text-green-800",
  yellow: "bg-yellow-100 text-yellow-800",
  red:    "bg-red-100 text-red-800",
  gray:   "bg-gray-100 text-gray-700",
  blue:   "bg-blue-100 text-blue-800",
  orange: "bg-orange-100 text-orange-800",
};

export function Badge({ variant = "gray", children }: BadgeProps) {
  return (
    <span
      className={clsx(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        variantClasses[variant],
      )}
    >
      {children}
    </span>
  );
}
