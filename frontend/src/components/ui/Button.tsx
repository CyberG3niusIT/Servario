import { clsx } from "clsx";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          "inline-flex items-center justify-center gap-2 rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
          size === "sm" ? "px-3 py-1.5 text-sm" : "px-4 py-2 text-sm",
          variant === "primary" &&
            "bg-brand-600 text-white hover:bg-brand-700",
          variant === "secondary" &&
            "bg-white text-gray-700 border border-gray-300 hover:bg-gray-50",
          variant === "danger" &&
            "bg-red-600 text-white hover:bg-red-700",
          variant === "ghost" &&
            "text-gray-600 hover:bg-gray-100",
          className,
        )}
        {...props}
      >
        {children}
      </button>
    );
  },
);
Button.displayName = "Button";
