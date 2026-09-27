import { cn } from "@/lib/utils";

type TrendAreaPoint = {
  label: string;
  value: number;
};

type TrendAreaChartProps = {
  id: string;
  points: TrendAreaPoint[];
  className?: string;
  rangeFormatter?: (value: number) => string;
};

const buildLinePath = (values: number[], width: number, height: number, padding: number) => {
  if (values.length < 2) return "";

  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const innerWidth = width - padding * 2;
  const innerHeight = height - padding * 2;
  const step = innerWidth / (values.length - 1);

  return values
    .map((value, index) => {
      const x = padding + index * step;
      const y = padding + innerHeight - ((value - min) / range) * innerHeight;
      return `${index === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
};

const buildAreaPath = (linePath: string, width: number, height: number, padding: number) => {
  if (!linePath) return "";
  return `${linePath} L ${width - padding} ${height - padding} L ${padding} ${height - padding} Z`;
};

const defaultRangeFormatter = (value: number) => value.toFixed(1);

export function TrendAreaChart({
  id,
  points,
  className,
  rangeFormatter = defaultRangeFormatter,
}: TrendAreaChartProps) {
  const chartWidth = 600;
  const chartHeight = 160;
  const chartPadding = 18;
  const values = points.map((point) => point.value);

  const minValue = values.length > 0 ? Math.min(...values) : 0;
  const maxValue = values.length > 0 ? Math.max(...values) : 0;
  const linePath = buildLinePath(values, chartWidth, chartHeight, chartPadding);
  const areaPath = buildAreaPath(linePath, chartWidth, chartHeight, chartPadding);

  return (
    <div className={cn("w-full overflow-hidden rounded-[var(--radius-surface)] border border-border/60 bg-background p-4", className)}>
      <div className="flex items-center justify-between text-[11px] text-muted-foreground">
        <span>{rangeFormatter(maxValue)}</span>
        <span>{rangeFormatter(minValue)}</span>
      </div>
      <svg
        className="mt-3 h-[160px] w-full"
        viewBox={`0 0 ${chartWidth} ${chartHeight}`}
        preserveAspectRatio="none"
        fill="none"
        aria-hidden="true"
      >
        <defs>
          <linearGradient id={`area-${id}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="hsl(var(--primary))" stopOpacity="0.14" />
            <stop offset="100%" stopColor="hsl(var(--primary))" stopOpacity="0" />
          </linearGradient>
        </defs>
        {areaPath ? <path d={areaPath} fill={`url(#area-${id})`} /> : null}
        {linePath ? (
          <path d={linePath} stroke="hsl(var(--primary))" strokeWidth="1.5" strokeLinecap="round" strokeOpacity="0.52" />
        ) : null}
      </svg>
      <div className="mt-2 flex items-center justify-between text-[11px] text-muted-foreground">
        {points.map((point) => (
          <span key={`${id}-${point.label}`} className="w-full text-center">
            {point.label}
          </span>
        ))}
      </div>
    </div>
  );
}
