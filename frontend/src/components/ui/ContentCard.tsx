"use client"

import { cn } from "@/lib/utils";

interface ContentCardProps {
  children: React.ReactNode;
  className?: string;
}

export function ContentCard({ children, className }: ContentCardProps) {
  return (
    <div
      className={cn(
        "rounded-[var(--radius-card)] border border-border/60 bg-card p-6",
        className
      )}
    >
      {children}
    </div>
  );
}
