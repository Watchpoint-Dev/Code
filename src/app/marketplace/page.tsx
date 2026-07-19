"use client";

import { useMemo, useState } from "react";
import { Filter, X } from "lucide-react";

import { PageHeader } from "@/app/components/ui/PageHeader";
import { ContentCard } from "@/app/components/ui/ContentCard";
import { Badge } from "@/app/components/ui/badge";
import { Button } from "@/app/components/ui/button";
import { Checkbox } from "@/app/components/ui/checkbox";
import { Input } from "@/app/components/ui/input";
import { SolidPlaceholder } from "@/app/components/ui/SolidPlaceholder";
import { Slider } from "@/app/components/ui/slider";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/app/components/ui/select";
import { marketplaceListings as watches } from "@/lib/dummy-data";
import { getFlagEmoji } from "@/lib/flags";

const Marketplace = () => {
  const filterOptions = useMemo(() => {
    const brands = new Set<string>();
    const conditions = new Set<string>();
    const movements = new Set<string>();
    const dials = new Set<string>();
    const straps = new Set<string>();
    const locations = new Set<string>();
    const sellers = new Set<string>();
    const caseSizes = new Set<number>();
    const prices: number[] = [];

    watches.forEach((watch) => {
      brands.add(watch.brand);
      conditions.add(watch.condition);
      movements.add(watch.movement);
      dials.add(watch.dial);
      straps.add(watch.strap);
      locations.add(watch.location);
      sellers.add(watch.seller);
      caseSizes.add(watch.caseSizeMm);
      prices.push(watch.price);
    });

    const sortAlpha = (valueA: string, valueB: string) => valueA.localeCompare(valueB);
    const sortedPrices = prices.sort((a, b) => a - b);

    return {
      brands: Array.from(brands).sort(sortAlpha),
      conditions: Array.from(conditions).sort(sortAlpha),
      movements: Array.from(movements).sort(sortAlpha),
      dials: Array.from(dials).sort(sortAlpha),
      straps: Array.from(straps).sort(sortAlpha),
      locations: Array.from(locations).sort(sortAlpha),
      sellers: Array.from(sellers).sort(sortAlpha),
      caseSizes: Array.from(caseSizes).sort((a, b) => a - b),
      priceMin: sortedPrices[0] ?? 0,
      priceMax: sortedPrices[sortedPrices.length - 1] ?? 0,
    };
  }, []);

  const [filtersOpen, setFiltersOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [priceRange, setPriceRange] = useState<[number, number]>(() => [
    filterOptions.priceMin,
    filterOptions.priceMax,
  ]);
  const [selectedBrands, setSelectedBrands] = useState<Set<string>>(() => new Set());
  const [selectedConditions, setSelectedConditions] = useState<Set<string>>(() => new Set());
  const [selectedCaseSize, setSelectedCaseSize] = useState<string>("");
  const [selectedMovement, setSelectedMovement] = useState<string>("");
  const [selectedDial, setSelectedDial] = useState<string>("");
  const [selectedStrap, setSelectedStrap] = useState<string>("");
  const [selectedLocation, setSelectedLocation] = useState<string>("");
  const [selectedSeller, setSelectedSeller] = useState<string>("");
  const [dateFrom, setDateFrom] = useState<string>("");
  const [dateTo, setDateTo] = useState<string>("");

  const formatCurrency = (value: number) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);

  const toggleSetValue = (setter: React.Dispatch<React.SetStateAction<Set<string>>>, value: string) => {
    setter((prev) => {
      const next = new Set(prev);
      if (next.has(value)) {
        next.delete(value);
      } else {
        next.add(value);
      }
      return next;
    });
  };

  const handlePriceInput = (index: 0 | 1, value: string) => {
    const parsed = Number(value);
    if (Number.isNaN(parsed)) return;
    setPriceRange((prev) => {
      const next: [number, number] = [...prev] as [number, number];
      next[index] = parsed;
      if (next[0] > next[1]) {
        return [next[1], next[0]];
      }
      return next;
    });
  };

  const normalizedQuery = searchQuery.trim().toLowerCase();
  const priceMin = priceRange[0];
  const priceMax = priceRange[1];

  const filteredWatches = useMemo(() => {
    const fromYear = dateFrom ? new Date(dateFrom).getFullYear() : null;
    const toYear = dateTo ? new Date(dateTo).getFullYear() : null;

    return watches.filter((watch) => {
      if (normalizedQuery) {
        const haystack = [
          watch.brand,
          watch.model,
          watch.reference,
          watch.description,
          watch.tags.join(" "),
        ]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(normalizedQuery)) {
          return false;
        }
      }

      if (watch.price < priceMin || watch.price > priceMax) return false;
      if (selectedBrands.size > 0 && !selectedBrands.has(watch.brand)) return false;
      if (selectedConditions.size > 0 && !selectedConditions.has(watch.condition)) return false;
      if (selectedCaseSize && String(watch.caseSizeMm) !== selectedCaseSize) return false;
      if (selectedMovement && watch.movement !== selectedMovement) return false;
      if (selectedDial && watch.dial !== selectedDial) return false;
      if (selectedStrap && watch.strap !== selectedStrap) return false;
      if (selectedLocation && watch.location !== selectedLocation) return false;
      if (selectedSeller && watch.seller !== selectedSeller) return false;
      if (fromYear && watch.year < fromYear) return false;
      if (toYear && watch.year > toYear) return false;

      return true;
    });
  }, [
    normalizedQuery,
    priceMin,
    priceMax,
    selectedBrands,
    selectedConditions,
    selectedCaseSize,
    selectedMovement,
    selectedDial,
    selectedStrap,
    selectedLocation,
    selectedSeller,
    dateFrom,
    dateTo,
  ]);

  const clearFilters = () => {
    setSearchQuery("");
    setPriceRange([filterOptions.priceMin, filterOptions.priceMax]);
    setSelectedBrands(new Set());
    setSelectedConditions(new Set());
    setSelectedCaseSize("");
    setSelectedMovement("");
    setSelectedDial("");
    setSelectedStrap("");
    setSelectedLocation("");
    setSelectedSeller("");
    setDateFrom("");
    setDateTo("");
  };

  const totalListings = watches.length;
  const featuredListings = watches.filter((watch) => watch.featured).length;
  const availableNow = watches.filter((watch) => watch.availability === "In Stock").length;
  const filteredCount = filteredWatches.length;

  return (
    <div>
      <PageHeader title="Marketplace" subtitle="Curated luxury watches from trusted sellers" />

      <div className="grid gap-4 sm:grid-cols-3">
        <ContentCard className="flex flex-col gap-2 border border-border/60 bg-card/80">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Total Listings</span>
          <p className="text-2xl font-semibold text-foreground">{totalListings}</p>
          <span className="text-xs text-muted-foreground">Across global partners</span>
        </ContentCard>
        <ContentCard className="flex flex-col gap-2 border border-border/60 bg-card/80">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Featured Picks</span>
          <p className="text-2xl font-semibold text-foreground">{featuredListings}</p>
          <span className="text-xs text-muted-foreground">Editor-curated highlights</span>
        </ContentCard>
        <ContentCard className="flex flex-col gap-2 border border-border/60 bg-card/80">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Available Now</span>
          <p className="text-2xl font-semibold text-foreground">{availableNow}</p>
          <span className="text-xs text-muted-foreground">Ready to ship today</span>
        </ContentCard>
      </div>

      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <p className="text-sm text-muted-foreground">
                {filteredCount} results · {featuredListings} featured · {availableNow} available
              </p>
            </div>
            <Button
              variant="outline"
              onClick={() => setFiltersOpen((open) => !open)}
              aria-expanded={filtersOpen}
              aria-controls="marketplace-filters"
            >
              {filtersOpen ? <X className="h-4 w-4" /> : <Filter className="h-4 w-4" />}
              {filtersOpen ? "Hide filters" : "Show filters"}
            </Button>
          </div>

          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {filteredWatches.map((watch) => (
              <ContentCard key={watch.id} className="flex h-full flex-col gap-4 border border-border/60">
                <div className="flex flex-wrap items-start gap-4">
                  <div className="aspect-square w-1/2 min-w-[140px] flex-shrink-0 overflow-hidden rounded-[var(--radius-surface)] bg-muted">
                    <SolidPlaceholder className="h-full w-full rounded-[var(--radius-surface)]" />
                  </div>
                  <div className="flex flex-1 flex-col justify-between gap-2">
                    <div>
                      <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{watch.brand}</p>
                      <h3 className="text-lg font-semibold text-foreground">{watch.model}</h3>
                      <p className="text-sm text-muted-foreground">{watch.reference}</p>
                    </div>
                    <div>
                      <p className="text-lg font-semibold text-foreground">
                        {new Intl.NumberFormat("en-US", {
                          style: "currency",
                          currency: watch.currency,
                          maximumFractionDigits: 0,
                        }).format(watch.price)}
                      </p>
                      <p className="text-xs text-muted-foreground">Listed {watch.year}</p>
                    </div>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  {watch.featured && <Badge>Featured</Badge>}
                  <Badge variant="secondary">{watch.condition}</Badge>
                  <Badge variant="outline">{watch.availability}</Badge>
                </div>

                <p className="text-sm text-muted-foreground">{watch.description}</p>

                <div className="grid grid-cols-2 gap-0 overflow-hidden rounded-[var(--radius-surface)] border border-border/70 text-sm text-muted-foreground">
                  <div className="border-b border-r border-border/60 p-3">
                    <span className="font-medium text-foreground">Case</span>
                    <div>{watch.caseSizeMm}mm · {watch.material}</div>
                  </div>
                  <div className="border-b border-border/60 p-3">
                    <span className="font-medium text-foreground">Movement</span>
                    <div>{watch.movement}</div>
                  </div>
                  <div className="border-r border-border/60 p-3">
                    <span className="font-medium text-foreground">Dial</span>
                    <div>{watch.dial}</div>
                  </div>
                  <div className="p-3">
                    <span className="font-medium text-foreground">Strap</span>
                    <div>{watch.strap}</div>
                  </div>
                </div>

                <div className="mt-auto flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground">
                  <span className="inline-flex items-center gap-2">
                    <span aria-hidden>{getFlagEmoji(watch.location)}</span>
                    <span>{watch.location}</span>
                  </span>
                  <span>Seller: {watch.seller}</span>
                </div>

                <div className="flex flex-wrap gap-2">
                  {watch.tags.map((tag) => (
                    <Badge key={`${watch.id}-${tag}`} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
              </ContentCard>
            ))}
          </div>
        </div>

        {filtersOpen ? (
          <aside
            id="marketplace-filters"
            className="w-full lg:w-[320px] lg:flex-shrink-0"
          >
            <ContentCard className="sticky top-6 flex flex-col gap-6 border border-border/60 bg-card/90 p-5">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Filters</p>
                <h2 className="text-lg font-semibold text-foreground">Refine listings</h2>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium text-foreground" htmlFor="marketplace-search">
                  Search
                </label>
                <Input
                  id="marketplace-search"
                  placeholder="Search brand, model, or reference"
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Price</span>
                  <span className="text-xs text-muted-foreground">
                    {formatCurrency(priceMin)} - {formatCurrency(priceMax)}
                  </span>
                </div>
                <Slider
                  value={[priceMin, priceMax]}
                  max={filterOptions.priceMax}
                  min={filterOptions.priceMin}
                  step={1000}
                  onValueChange={(value) => setPriceRange([value[0], value[1]])}
                />
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    type="number"
                    placeholder="Min"
                    value={priceMin}
                    onChange={(event) => handlePriceInput(0, event.target.value)}
                  />
                  <Input
                    type="number"
                    placeholder="Max"
                    value={priceMax}
                    onChange={(event) => handlePriceInput(1, event.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Brands</span>
                <div className="space-y-2">
                  {filterOptions.brands.map((brand) => (
                    <label key={brand} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Checkbox
                        checked={selectedBrands.has(brand)}
                        onCheckedChange={() => toggleSetValue(setSelectedBrands, brand)}
                      />
                      <span>{brand}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Condition</span>
                <div className="space-y-2">
                  {filterOptions.conditions.map((condition) => (
                    <label key={condition} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Checkbox
                        checked={selectedConditions.has(condition)}
                        onCheckedChange={() => toggleSetValue(setSelectedConditions, condition)}
                      />
                      <span>{condition}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Specs</span>
                <div className="space-y-3">
                  <Select
                    value={selectedCaseSize || "any"}
                    onValueChange={(value) => setSelectedCaseSize(value === "any" ? "" : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Case size" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any case size</SelectItem>
                      {filterOptions.caseSizes.map((size) => (
                        <SelectItem key={size} value={String(size)}>
                          {size}mm
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select
                    value={selectedMovement || "any"}
                    onValueChange={(value) => setSelectedMovement(value === "any" ? "" : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Movement" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any movement</SelectItem>
                      {filterOptions.movements.map((movement) => (
                        <SelectItem key={movement} value={movement}>
                          {movement}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select
                    value={selectedDial || "any"}
                    onValueChange={(value) => setSelectedDial(value === "any" ? "" : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Dial" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any dial</SelectItem>
                      {filterOptions.dials.map((dial) => (
                        <SelectItem key={dial} value={dial}>
                          {dial}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <Select
                    value={selectedStrap || "any"}
                    onValueChange={(value) => setSelectedStrap(value === "any" ? "" : value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Strap" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="any">Any strap</SelectItem>
                      {filterOptions.straps.map((strap) => (
                        <SelectItem key={strap} value={strap}>
                          {strap}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Location</span>
                <Select
                  value={selectedLocation || "any"}
                  onValueChange={(value) => setSelectedLocation(value === "any" ? "" : value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any location" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any location</SelectItem>
                    {filterOptions.locations.map((location) => (
                      <SelectItem key={location} value={location}>
                        {location}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Date listed</span>
                <div className="grid grid-cols-2 gap-3">
                  <Input type="date" value={dateFrom} onChange={(event) => setDateFrom(event.target.value)} />
                  <Input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value)} />
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Seller</span>
                <Select
                  value={selectedSeller || "any"}
                  onValueChange={(value) => setSelectedSeller(value === "any" ? "" : value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any seller" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any seller</SelectItem>
                    {filterOptions.sellers.map((seller) => (
                      <SelectItem key={seller} value={seller}>
                        {seller}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex gap-2">
                <Button variant="default" className="flex-1" onClick={() => setFiltersOpen(false)}>
                  Apply filters
                </Button>
                <Button variant="outline" className="flex-1" onClick={clearFilters}>
                  Clear
                </Button>
              </div>
            </ContentCard>
          </aside>
        ) : null}
      </div>
    </div>
  );
};

export default Marketplace;
