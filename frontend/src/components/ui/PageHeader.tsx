"use client"

interface PageHeaderProps {
  title: string;
  description?: string;
  subtitle?: string;
}

export function PageHeader({ title, description, subtitle }: PageHeaderProps) {
  const secondary = subtitle ?? description;

  return (
    <div className="mb-6">
      <h1 className="text-2xl font-semibold text-foreground">{title}</h1>
      {secondary && (
        <p className="mt-1 text-muted-foreground">{secondary}</p>
      )}
    </div>
  );
}
