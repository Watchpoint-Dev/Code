import Link from "next/link";
import { notFound } from "next/navigation";
import {
  ArrowUpRight,
  Eye,
  Gauge,
  Layers,
  Plus,
  ShieldCheck,
  Tag,
  Waves,
} from "lucide-react";

import { Badge, type BadgeProps } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ContentCard } from "@/components/ui/ContentCard";
import { TrendAreaChart } from "@/components/ui/TrendAreaChart";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { watchInsightById } from "@/lib/watch-insights";

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const formatPercent = (value: number) => `${value >= 0 ? "+" : ""}${value.toFixed(2)}%`;

const getBadgeTone = (value: number): BadgeProps["variant"] => {
  if (value >= 12) return "success";
  if (value >= 6) return "info";
  if (value >= 0) return "warning";
  return "danger";
};

type WatchInsightPageProps = {
  params: Promise<{
    watchid: string;
  }>;
};

export default async function WatchInsightPage({ params }: WatchInsightPageProps) {
  const { watchid } = await params;
  const watch = watchInsightById.get(watchid);

  if (!watch) notFound();

  const premiumPct = ((watch.marketPrice - watch.retailPriceUsd) / watch.retailPriceUsd) * 100;
  const performanceRows = [
    { label: "3M", value: watch.performance["3m"] },
    { label: "6M", value: watch.performance["6m"] },
    { label: "1Y", value: watch.performance["1y"] },
    { label: "2Y", value: watch.performance["2y"] },
  ];

  const specRows = [
    { label: "Reference", value: watch.reference, info: "Dataset ID" },
    { label: "Segment", value: watch.segment, info: "Market bucket" },
    { label: "Material", value: watch.material, info: "Case material" },
    { label: "Movement", value: watch.movement, info: watch.caliber },
    { label: "Diameter", value: `${watch.caseSizeMm} mm`, info: "Case size" },
    { label: "Water Resistance", value: `${watch.waterResistanceM} m`, info: "Pressure rated" },
    { label: "Dial", value: watch.dial, info: "Primary color" },
    { label: "Crystal", value: watch.crystal, info: "Front glass" },
    { label: "Complication", value: watch.complication, info: "Main function" },
    { label: "Power Reserve", value: `${watch.powerReserveHours} h`, info: "Autonomy" },
  ];

  return (
    <div className="space-y-6">
      <ContentCard className="overflow-hidden border border-border/60 bg-gradient-to-br from-card via-card to-muted/40 p-0">
        <div className="grid gap-0 lg:grid-cols-[320px_1fr]">
          <aside className="border-b border-border/60 p-5 lg:border-b-0 lg:border-r">
            <div className="rounded-[var(--radius-surface)] border border-border/70 bg-background/70 p-4">
              <div className="relative flex aspect-square items-center justify-center overflow-hidden rounded-[var(--radius-surface)] border border-border/60 bg-gradient-to-b from-muted/50 via-background to-muted/40">
                <div className="absolute -left-8 top-8 h-28 w-28 rounded-full bg-sky-400/10 blur-2xl" aria-hidden="true" />
                <div className="absolute -right-8 bottom-4 h-24 w-24 rounded-full bg-indigo-400/10 blur-2xl" aria-hidden="true" />
                <div className="text-center">
                  <p className="text-xs uppercase tracking-[0.22em] text-muted-foreground">{watch.brand}</p>
                  <p className="mt-2 text-3xl font-semibold leading-tight text-foreground">{watch.model}</p>
                  <p className="mt-2 text-sm text-muted-foreground">Ref. {watch.reference}</p>
                  <Badge variant="neutral" className="mt-4">
                    {watch.segment}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="mt-4 space-y-3">
              <Button className="h-11 w-full">
                <Plus className="h-4 w-4" />
                Add to Assets
              </Button>
              <div className="grid grid-cols-2 gap-3">
                <Button asChild variant="outline" className="h-11">
                  <Link href="/auctions">
                    <Eye className="h-4 w-4" />
                    Auctions
                  </Link>
                </Button>
                <Button asChild variant="outline" className="h-11">
                  <Link href="/marketplace">
                    <Tag className="h-4 w-4" />
                    Sales
                  </Link>
                </Button>
              </div>
            </div>
          </aside>

          <section className="p-5 lg:p-6">
            <div className="flex flex-wrap items-start justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Watch Insights</p>
                <h1 className="mt-2 text-3xl font-semibold text-foreground lg:text-4xl">{watch.model}</h1>
                <div className="mt-3 flex flex-wrap items-center gap-2">
                  <Badge variant="secondary">{watch.brand}</Badge>
                  <Badge variant="neutral">#{watch.reference}</Badge>
                  <Badge variant="success">
                    {watch.activeListings} active listings
                  </Badge>
                </div>
              </div>

              <div className="rounded-[var(--radius-surface)] border border-border/70 bg-background/70 px-4 py-3 text-right">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Current Market Value</p>
                <p className="mt-1 text-3xl font-semibold text-foreground">{formatCurrency(watch.marketPrice)}</p>
                <p className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-emerald-600">
                  USD
                  <ArrowUpRight className="h-3.5 w-3.5" />
                </p>
              </div>
            </div>

            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <div className="rounded-[var(--radius-surface)] border border-border/70 bg-background/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Retail Price</p>
                <p className="mt-2 text-2xl font-semibold text-foreground">{formatCurrency(watch.retailPriceUsd)}</p>
                <p className="mt-1 text-xs text-muted-foreground">Manufacturer suggested retail</p>
              </div>

              <div className="rounded-[var(--radius-surface)] border border-border/70 bg-background/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Premium vs Retail</p>
                <p className="mt-2 text-2xl font-semibold text-foreground">{formatPercent(premiumPct)}</p>
                <Badge variant={getBadgeTone(premiumPct)} className="mt-2">
                  {premiumPct >= 0 ? "Above retail" : "Below retail"}
                </Badge>
              </div>

              <div className="rounded-[var(--radius-surface)] border border-border/70 bg-background/70 p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Performance Index</p>
                <p className="mt-2 text-2xl font-semibold text-foreground">{watch.performanceIndex.toFixed(2)}</p>
                <p className="mt-1 text-xs text-muted-foreground">Composite momentum signal</p>
              </div>
            </div>
          </section>
        </div>
      </ContentCard>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <ContentCard className="border border-border/60 p-5 lg:p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Performance</p>
              <h2 className="mt-1 text-xl font-semibold text-foreground">Price Momentum</h2>
            </div>
            <Badge variant={getBadgeTone(watch.performance["1y"])}>
              {formatPercent(watch.performance["1y"])} over 1Y
            </Badge>
          </div>

          <TrendAreaChart
            id={`watch-insight-${watch.id}`}
            points={performanceRows}
            className="mt-4"
            rangeFormatter={(value) => `${value.toFixed(2)}%`}
          />
        </ContentCard>

        <ContentCard className="border border-border/60 p-5 lg:p-6">
          <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Quick Facts</p>
          <h2 className="mt-1 text-xl font-semibold text-foreground">At a Glance</h2>

          <div className="mt-4 grid gap-3 sm:grid-cols-3">
            <div className="rounded-[var(--radius-surface)] border border-border/60 bg-background/70 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <ShieldCheck className="h-4 w-4" />
                <span className="text-xs uppercase tracking-[0.16em]">Water Resistance</span>
              </div>
              <p className="mt-2 text-lg font-semibold text-foreground">{watch.waterResistanceM} m</p>
            </div>
            <div className="rounded-[var(--radius-surface)] border border-border/60 bg-background/70 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Gauge className="h-4 w-4" />
                <span className="text-xs uppercase tracking-[0.16em]">Power Reserve</span>
              </div>
              <p className="mt-2 text-lg font-semibold text-foreground">{watch.powerReserveHours} h</p>
            </div>
            <div className="rounded-[var(--radius-surface)] border border-border/60 bg-background/70 p-3">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Layers className="h-4 w-4" />
                <span className="text-xs uppercase tracking-[0.16em]">Case Size</span>
              </div>
              <p className="mt-2 text-lg font-semibold text-foreground">{watch.caseSizeMm} mm</p>
            </div>
          </div>

          <div className="mt-3 rounded-[var(--radius-surface)] border border-border/60 bg-background/70 p-3">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Waves className="h-4 w-4" />
              <span className="text-xs uppercase tracking-[0.16em]">Caliber</span>
            </div>
            <p className="mt-2 text-base font-semibold text-foreground">{watch.caliber}</p>
          </div>
        </ContentCard>
      </div>

      <Table>
        <TableHeader>
          <TableRow className="hover:bg-transparent">
            <TableHead className="w-[40%]">Specification</TableHead>
            <TableHead className="w-[30%]">Details</TableHead>
            <TableHead className="w-[30%]">Additional Info</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {specRows.map((row) => (
            <TableRow key={row.label}>
              <TableCell className="font-medium text-foreground">{row.label}</TableCell>
              <TableCell className="text-foreground">{row.value}</TableCell>
              <TableCell className="text-muted-foreground">{row.info}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
