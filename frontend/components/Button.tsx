import React from "react";
import { Loader2 } from "lucide-react";

export type ButtonVariant =
  | "primary"
  | "secondary"
  | "ghost"
  | "destructive"
  | "accent";

export type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className = "",
      variant = "primary",
      size = "md",
      isLoading = false,
      leftIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      "inline-flex items-center justify-center font-medium rounded-sm transition-colors focus:outline-none focus:ring-2 focus:ring-brand-300 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

    const variantStyles: Record<ButtonVariant, string> = {
      primary: "bg-brand-600 text-white hover:bg-brand-700 border border-transparent",
      secondary: "bg-transparent text-slate-700 border border-slate-300 hover:bg-slate-50",
      ghost: "bg-transparent text-brand-600 hover:bg-brand-50 border border-transparent",
      destructive: "bg-error-600 text-white hover:bg-red-700 border border-transparent",
      accent: "bg-accent-500 text-white hover:bg-accent-600 border border-transparent",
    };

    const sizeStyles: Record<ButtonSize, string> = {
      sm: "h-[32px] px-3 text-sm",
      md: "h-[40px] px-4 text-sm",
      lg: "h-[48px] px-6 text-base",
    };

    const combinedClassName = `${baseStyles} ${variantStyles[variant]} ${sizeStyles[size]} ${className}`;

    return (
      <button
        ref={ref}
        className={combinedClassName}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
        {!isLoading && leftIcon && <span className="mr-2">{leftIcon}</span>}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";
