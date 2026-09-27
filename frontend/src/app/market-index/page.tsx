import { PageHeader } from "@/components/ui/PageHeader";
import { ContentCard } from "@/components/ui/ContentCard";
import { Badge } from "@/components/ui/badge";
import { SolidPlaceholder } from "@/components/ui/SolidPlaceholder";
import { TrendAreaChart } from "@/components/ui/TrendAreaChart";
import brandIndices from "@/fixtures/market-index/brand-indices.json";

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const MarketIndex = () => {
  return (
    <div>
      <PageHeader title="Market Index" subtitle="Brand indices tracking the hottest references" />

      <div className="grid gap-6 lg:grid-cols-2">
        {brandIndices.map((index) => {
          const isPositive = index.changePct >= 0;
          const badgeVariant = isPositive ? "success" : "danger";
          const minValue = Math.min(...index.sparkline);
          const maxValue = Math.max(...index.sparkline);
          const monthLabels = ["Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan"];
          const trendPoints = index.sparkline.map((value, position) => ({
            label: monthLabels[position] ?? `P${position + 1}`,
            value,
          }));

          return (
            <ContentCard
              key={index.id}
              className="relative overflow-hidden border border-border/60 bg-card/90"
            >
              <div className="relative flex items-start justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
                    {index.category}
                  </p>
                  <h2 className="mt-2 text-xl font-semibold text-foreground">
                    {index.brand} Index
                  </h2>
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <span className="text-3xl font-semibold text-foreground">
                      {index.indexValue.toFixed(1)}
                    </span>
                    <Badge variant={badgeVariant}>
                      {isPositive ? "+" : ""}
                      {index.changePct.toFixed(2)}%
                    </Badge>
                    <span className="text-xs text-muted-foreground">{index.period} change</span>
                  </div>
                </div>

                <div className="ml-auto text-right">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
                    Range
                  </p>
                  <p className="mt-2 text-sm font-semibold text-foreground">
                    {minValue.toFixed(1)} — {maxValue.toFixed(1)}
                  </p>
                </div>
              </div>

              <div className="relative mt-6">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  <span>Index Trend</span>
                  <span>{index.period}</span>
                </div>
                <TrendAreaChart id={`market-index-${index.id}`} points={trendPoints} className="mt-4" />
              </div>

              <div className="relative mt-6">
                <div className="flex items-center justify-between text-xs uppercase tracking-[0.2em] text-muted-foreground">
                  <span>Top Models</span>
                  <span>{index.watches.length} listings</span>
                </div>

                <div className="scroll-area-light mt-4 max-h-72 space-y-3 overflow-y-auto pr-2">
                  {index.watches.map((watch) => (
                    <div
                      key={watch.id}
                      className="flex items-center gap-3 rounded-[var(--radius-surface)]"
                    >
                      <div className="h-12 w-12 overflow-hidden rounded-[var(--radius-surface)] bg-muted">
                        <SolidPlaceholder className="h-full w-full" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-foreground">{watch.model}</p>
                        <p className="text-xs text-muted-foreground">
                          {watch.reference} · {watch.year}
                        </p>
                      </div>
                      <p className="text-sm font-semibold text-foreground">
                        {formatCurrency(watch.price)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </ContentCard>
          );
        })}
      </div>
    </div>
  );
};

export default MarketIndex;
