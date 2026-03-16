interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  className?: string;
}

const sizes = { sm: "w-4 h-4", md: "w-8 h-8", lg: "w-12 h-12" };

export function LoadingSpinner({ size = "md", className = "" }: LoadingSpinnerProps) {
  return (
    <div
      className={`${sizes[size]} border-4 border-yu-gold-500 border-t-transparent rounded-full animate-spin ${className}`}
      role="status"
      aria-label="Loading"
    />
  );
}

export function FullPageSpinner() {
  return (
    <div className="flex items-center justify-center h-40">
      <LoadingSpinner size="lg" />
    </div>
  );
}
