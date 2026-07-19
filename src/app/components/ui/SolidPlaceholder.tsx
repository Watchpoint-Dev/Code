"use client";

import { cn } from "@/lib/utils";

type SolidPlaceholderProps = React.HTMLAttributes<HTMLDivElement>;

const SolidPlaceholder = ({ className, ...props }: SolidPlaceholderProps) => {
  return <div className={cn("rounded-[inherit] bg-muted", className)} aria-hidden="true" {...props} />;
};

export { SolidPlaceholder };
