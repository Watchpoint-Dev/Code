"use client";

import { useMemo, useState } from "react";
import { Plus, X } from "lucide-react";

import { PageHeader } from "@/app/components/ui/PageHeader";
import { ContentCard } from "@/app/components/ui/ContentCard";
import { Button } from "@/app/components/ui/button";
import { SolidPlaceholder } from "@/app/components/ui/SolidPlaceholder";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/app/components/ui/command";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/app/components/ui/dialog";
import { marketWatches, type HydratedMarketWatch } from "@/lib/market-data";

const MAX_COMPARE = 4;
const SLOT_WIDTH = "w-[450px] min-w-[450px]";
const watchById = new Map(marketWatches.map((watch) => [watch.id, watch]));

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const buildRows = (watch: HydratedMarketWatch) => [
  { label: "Reference", value: watch.reference },
  { label: "Market value", value: formatCurrency(watch.marketValueUsd) },
  { label: "Production year", value: String(watch.productionYear) },
  { label: "Case", value: `${watch.caseSizeMm}mm · ${watch.caseMaterial}` },
  { label: "Dial", value: watch.dialColor },
  { label: "Movement", value: watch.movementType },
  { label: "Bracelet", value: watch.braceletType },
];

const Compare = () => {
  const [selectedWatchIds, setSelectedWatchIds] = useState<string[]>([]);
  const [isPickerOpen, setIsPickerOpen] = useState(false);

  const selectedIdSet = useMemo(() => new Set(selectedWatchIds), [selectedWatchIds]);
  const selectedWatches = selectedWatchIds
    .map((watchId) => watchById.get(watchId))
    .filter((watch): watch is HydratedMarketWatch => Boolean(watch));

  const availableWatches = useMemo(
    () => marketWatches.filter((watch) => !selectedIdSet.has(watch.id)),
    [selectedIdSet]
  );

  const firstEmptySlotIndex = selectedWatches.length < MAX_COMPARE ? selectedWatches.length : -1;

  const slots = Array.from({ length: MAX_COMPARE }, (_, index) => {
    const watch = selectedWatches[index] ?? null;
    return {
      key: watch?.id ?? `empty-slot-${index}`,
      watch,
      canAdd: index === firstEmptySlotIndex,
    };
  });

  const addWatch = (watchId: string) => {
    setSelectedWatchIds((prev) => {
      if (prev.includes(watchId) || prev.length >= MAX_COMPARE) return prev;
      return [...prev, watchId];
    });
    setIsPickerOpen(false);
  };

  const removeWatch = (watchId: string) => {
    setSelectedWatchIds((prev) => prev.filter((id) => id !== watchId));
  };

  const clearComparison = () => {
    setSelectedWatchIds([]);
  };

  return (
    <div>
      <PageHeader title="Compare" subtitle="Compare up to 4 watches with normalized market data references." />

      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <p className="text-sm text-muted-foreground">
          {selectedWatches.length}/{MAX_COMPARE} selected · {marketWatches.length} watches in dataset
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={() => setIsPickerOpen(true)}
            disabled={selectedWatches.length >= MAX_COMPARE || availableWatches.length === 0}
          >
            <Plus className="h-4 w-4" />
            Add watch
          </Button>
          <Button variant="outline" onClick={clearComparison} disabled={selectedWatches.length === 0}>
            Clear
          </Button>
        </div>
      </div>

      <div className="overflow-x-auto pb-2">
        <div className="flex w-max gap-4">
          {slots.map((slot, index) =>
            slot.watch ? (
              <ContentCard
                key={slot.key}
                className={`${SLOT_WIDTH} flex-shrink-0 border border-border/70 bg-card p-4`}
              >
                <div className="relative">
                  <div className="relative aspect-square w-full overflow-hidden rounded-2xl bg-muted">
                    <SolidPlaceholder className="h-full w-full rounded-2xl" />
                  </div>
                  <Button
                    size="icon"
                    variant="secondary"
                    className="absolute right-2 top-2"
                    onClick={() => removeWatch(slot.watch.id)}
                    aria-label={`Remove ${slot.watch.brandName} ${slot.watch.modelName}`}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>

                <div className="mt-4">
                  <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{slot.watch.brandName}</p>
                  <h2 className="text-lg font-semibold text-foreground">{slot.watch.modelName}</h2>
                  <p className="text-sm text-muted-foreground">
                    {slot.watch.collection} · {slot.watch.complication}
                  </p>
                </div>

                <div className="mt-4 overflow-hidden rounded-2xl border border-border/70">
                  <div className="divide-y divide-border/60">
                    {buildRows(slot.watch).map((row) => (
                      <div key={`${slot.watch.id}-${row.label}`} className="grid grid-cols-[135px_1fr] gap-3 p-3 text-sm">
                        <span className="text-muted-foreground">{row.label}</span>
                        <span className="font-medium text-foreground">{row.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </ContentCard>
            ) : (
              <ContentCard
                key={slot.key}
                className={`${SLOT_WIDTH} flex-shrink-0 border border-dashed border-border/70 bg-muted/30 p-4`}
              >
                <div className="aspect-square w-full rounded-2xl border border-dashed border-border/70 bg-muted/40" />
                <div className="mt-4 flex h-[370px] flex-col justify-between rounded-2xl border border-dashed border-border/70 p-4">
                  <div>
                    <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Comparison slot</p>
                    <h2 className="mt-1 text-lg font-semibold text-foreground">Slot {index + 1}</h2>
                    <p className="mt-2 text-sm text-muted-foreground">Add a watch to populate this comparison board.</p>
                  </div>

                  {slot.canAdd ? (
                    <Button
                      onClick={() => setIsPickerOpen(true)}
                      disabled={availableWatches.length === 0}
                      className="w-full"
                    >
                      <Plus className="h-4 w-4" />
                      Add watch to compare
                    </Button>
                  ) : (
                    <p className="text-sm text-muted-foreground">Waiting for the previous slot to be filled.</p>
                  )}
                </div>
              </ContentCard>
            )
          )}
        </div>
      </div>

      <Dialog open={isPickerOpen} onOpenChange={setIsPickerOpen}>
        <DialogContent className="max-w-2xl gap-6 p-8">
          <DialogHeader>
            <DialogTitle>Select watch to compare</DialogTitle>
            <DialogDescription>
              Data is resolved through `brandId` and `modelId` references from `brands.json` and `models.json`.
            </DialogDescription>
          </DialogHeader>

          <Command className="rounded-[24px] border border-border/70">
            <CommandInput placeholder="Search by brand, model, or reference" />
            <CommandList>
              <CommandEmpty>No watches available to add.</CommandEmpty>
              <CommandGroup heading="Available watches">
                {availableWatches.map((watch) => (
                  <CommandItem
                    key={watch.id}
                    value={`${watch.brandName} ${watch.modelName} ${watch.reference}`}
                    onSelect={() => addWatch(watch.id)}
                    className="flex items-center justify-between gap-4 rounded-2xl px-3 py-3"
                  >
                    <div className="flex min-w-0 items-center gap-3">
                      <div className="h-12 w-12 shrink-0 rounded-xl bg-muted" aria-hidden="true" />
                      <span className="min-w-0">
                        <span className="block truncate text-sm font-medium text-foreground">
                          {watch.brandName} {watch.modelName}
                        </span>
                        <span className="block truncate text-xs text-muted-foreground">{watch.reference}</span>
                      </span>
                    </div>
                    <span className="shrink-0 text-xs font-semibold text-foreground">
                      {formatCurrency(watch.marketValueUsd)}
                    </span>
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Compare;
