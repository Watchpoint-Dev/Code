"use client";

import { useMemo, useState } from "react";

import { PageHeader } from "@/app/components/ui/PageHeader";
import { ContentCard } from "@/app/components/ui/ContentCard";
import { Badge } from "@/app/components/ui/badge";
import { SolidPlaceholder } from "@/app/components/ui/SolidPlaceholder";
import { Slider } from "@/app/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { topPerformerWatches } from "@/lib/dummy-data";

interface WatchPerformance {
  "3m": number;
  "6m": number;
  "1y": number;
  "2y": number;
}

interface WatchEntry {
  id: string;
  brand: string;
  model: string;
  reference: string;
  segment: string;
  year: number;
  caseSizeMm: number;
  material: string;
  dial: string;
  movement: string;
  marketPrice: number;
  currency: string;
  performance: WatchPerformance;
}

type PerformanceKey = keyof WatchPerformance;

const periodOptions: { value: PerformanceKey; label: string }[] = [
  { value: "3m", label: "3 months" },
  { value: "6m", label: "6 months" },
  { value: "1y", label: "1 year" },
  { value: "2y", label: "2 years" },
];

const thresholdOptions = [5, 10, 15, 20, 30, 50];

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const formatPercent = (value: number) => `${value >= 0 ? "+" : ""}${value.toFixed(1)}%`;

const TopPerformers = () => {
  const watches = topPerformerWatches as WatchEntry[];

  const filterOptions = useMemo(() => {
    const brands = new Set<string>();
    const prices = watches.map((watch) => watch.marketPrice);

    watches.forEach((watch) => brands.add(watch.brand));

    const sortedPrices = [...prices].sort((a, b) => a - b);

    return {
      brands: Array.from(brands).sort((a, b) => a.localeCompare(b)),
      priceMin: sortedPrices[0] ?? 0,
      priceMax: sortedPrices[sortedPrices.length - 1] ?? 0,
    };
  }, [watches]);

  const [selectedBrand, setSelectedBrand] = useState<string>("all");
  const [minPrice, setMinPrice] = useState<number>(filterOptions.priceMin);
  const [performanceFloor, setPerformanceFloor] = useState<number>(10);
  const [period, setPeriod] = useState<PerformanceKey>("1y");

  const filtered = useMemo(() => {
    return watches.filter((watch) => {
      if (selectedBrand !== "all" && watch.brand !== selectedBrand) return false;
      if (watch.marketPrice < minPrice) return false;
      if (watch.performance[period] < performanceFloor) return false;
      return true;
    });
  }, [minPrice, performanceFloor, period, selectedBrand, watches]);

  const topResults = useMemo(() => {
    return [...filtered]
      .sort((a, b) => b.performance[period] - a.performance[period])
      .slice(0, 30);
  }, [filtered, period]);

  const activePeriodLabel = periodOptions.find((option) => option.value === period)?.label ?? "1 year";
  const maxPerformance = Math.max(...watches.map((watch) => watch.performance[period]));

  return (
    <div>
      <PageHeader title="Top Performers" subtitle="Discover the best-performing assets" />

      <ContentCard className="border border-border/60 bg-card/90">
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Discover Top Performers
            </p>
            <h2 className="mt-2 text-lg font-semibold text-foreground">
              Refine the strongest market movers
            </h2>
            <p className="mt-2 text-sm text-muted-foreground">
              {topResults.length} results · showing top 30 by {activePeriodLabel}
            </p>
          </div>
          <div className="text-right">
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">
              Peak Performance
            </p>
            <p className="mt-2 text-2xl font-semibold text-foreground">
              {formatPercent(maxPerformance)}
            </p>
          </div>
        </div>

        <div className="mt-6 grid gap-4 lg:grid-cols-4">
          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">See watches from</p>
            <Select value={selectedBrand} onValueChange={setSelectedBrand}>
              <SelectTrigger>
                <SelectValue placeholder="All Brands" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Brands</SelectItem>
                {filterOptions.brands.map((brand) => (
                  <SelectItem key={brand} value={brand}>
                    {brand}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
              With a market price above
            </p>
            <div className="rounded-[var(--radius-surface)] border border-border/60 bg-background px-4 py-3">
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium text-foreground">{formatCurrency(minPrice)}</span>
                <Badge variant="neutral">USD</Badge>
              </div>
              <Slider
                className="mt-3"
                min={filterOptions.priceMin}
                max={filterOptions.priceMax}
                step={100}
                value={[minPrice]}
                onValueChange={(value) => setMinPrice(value[0])}
              />
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">
              That are up more than
            </p>
            <Select value={String(performanceFloor)} onValueChange={(value) => setPerformanceFloor(Number(value))}>
              <SelectTrigger>
                <SelectValue placeholder="10%" />
              </SelectTrigger>
              <SelectContent>
                {thresholdOptions.map((threshold) => (
                  <SelectItem key={threshold} value={String(threshold)}>
                    {threshold}%
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">In the past</p>
            <Select value={period} onValueChange={(value) => setPeriod(value as PerformanceKey)}>
              <SelectTrigger>
                <SelectValue placeholder="1 year" />
              </SelectTrigger>
              <SelectContent>
                {periodOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </ContentCard>

      <div className="mt-8">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-muted-foreground">Results</p>
            <h3 className="mt-2 text-xl font-semibold text-foreground">Top Performing References</h3>
          </div>
          <span className="text-xs text-muted-foreground">
            {topResults.length} watches · top 30 of {filtered.length}
          </span>
        </div>

        <div className="mt-6 grid gap-6 md:grid-cols-2 xl:grid-cols-3">
          {topResults.map((watch) => {
            const change = watch.performance[period];
            const changeBadge = change >= 0 ? "success" : "danger";

            return (
              <ContentCard key={watch.id} className="border border-border/60 bg-card/90">
                <div className="flex items-stretch gap-4">
                  <div className="w-20 overflow-hidden rounded-[var(--radius-surface)] bg-muted">
                    <SolidPlaceholder className="h-full w-full rounded-[var(--radius-surface)]" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <h4 className="truncate text-base font-semibold text-foreground">
                      {watch.brand} — {watch.model}
                    </h4>
                    <p className="mt-1 text-xs text-muted-foreground">Ref. {watch.reference}</p>
                    <div className="mt-3 flex flex-wrap items-center gap-2">
                      <span className="text-sm font-semibold text-foreground">
                        {formatCurrency(watch.marketPrice)}
                      </span>
                      <Badge variant="neutral">USD</Badge>
                      <Badge variant={changeBadge}>{formatPercent(change)}</Badge>
                    </div>
                    <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                      <span>{watch.segment}</span>
                      <span>·</span>
                      <span>{watch.caseSizeMm}mm</span>
                      <span>·</span>
                      <span>{watch.material}</span>
                    </div>
                  </div>
                </div>
              </ContentCard>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TopPerformers;
