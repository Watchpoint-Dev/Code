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
import auctionsData from "@/data/dummy-data/auctions/auctions.json";
import { getFlagEmoji } from "@/lib/flags";

interface AuctionItem {
  id: string;
  auctionHouseId: string;
  auctionHouseName: string;
  location: string;
  lotNumber: number;
  imageUrl: string;
  endDate: string;
  startDate: string;
  currentBid: number;
  estimation: string;
  brand: string;
  model: string;
}

const auctions = auctionsData as AuctionItem[];

const getStatus = (auction: AuctionItem) => {
  const now = new Date();
  const start = new Date(auction.startDate);
  const end = new Date(auction.endDate);

  if (now < start) return "Upcoming";
  if (now > end) return "Closed";
  return "Live";
};

const getStatusVariant = (status: "Upcoming" | "Closed" | "Live") => {
  if (status === "Live") return "success";
  if (status === "Upcoming") return "secondary";
  return "outline";
};

const formatCurrency = (value: number) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);

const Auctions = () => {
  const filterOptions = useMemo(() => {
    const houses = new Set<string>();
    const brands = new Set<string>();
    const locations = new Set<string>();
    const bids: number[] = [];

    auctions.forEach((auction) => {
      houses.add(auction.auctionHouseName);
      brands.add(auction.brand);
      locations.add(auction.location);
      bids.push(auction.currentBid);
    });

    const sortedBids = bids.sort((a, b) => a - b);
    const sortAlpha = (a: string, b: string) => a.localeCompare(b);

    return {
      houses: Array.from(houses).sort(sortAlpha),
      brands: Array.from(brands).sort(sortAlpha),
      locations: Array.from(locations).sort(sortAlpha),
      bidMin: sortedBids[0] ?? 0,
      bidMax: sortedBids[sortedBids.length - 1] ?? 0,
    };
  }, []);

  const [filtersOpen, setFiltersOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [bidRange, setBidRange] = useState<[number, number]>(() => [filterOptions.bidMin, filterOptions.bidMax]);
  const [selectedHouses, setSelectedHouses] = useState<Set<string>>(() => new Set());
  const [selectedBrand, setSelectedBrand] = useState("");
  const [selectedLocation, setSelectedLocation] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [startFrom, setStartFrom] = useState("");
  const [endTo, setEndTo] = useState("");

  const toggleSetValue = (
    setter: (updater: (prev: Set<string>) => Set<string>) => void,
    value: string,
  ) => {
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

  const handleBidInput = (index: 0 | 1, value: string) => {
    const parsed = Number(value);
    if (Number.isNaN(parsed)) return;

    setBidRange((prev) => {
      const next: [number, number] = [...prev] as [number, number];
      next[index] = parsed;
      if (next[0] > next[1]) {
        return [next[1], next[0]];
      }
      return next;
    });
  };

  const normalizedQuery = searchQuery.trim().toLowerCase();
  const bidMin = bidRange[0];
  const bidMax = bidRange[1];

  const filteredAuctions = useMemo(() => {
    const startFromDate = startFrom ? new Date(startFrom) : null;
    const endToDate = endTo ? new Date(endTo) : null;

    return auctions.filter((auction) => {
      if (normalizedQuery) {
        const haystack = [auction.brand, auction.model, auction.auctionHouseName, `Lot ${auction.lotNumber}`]
          .join(" ")
          .toLowerCase();
        if (!haystack.includes(normalizedQuery)) return false;
      }

      if (auction.currentBid < bidMin || auction.currentBid > bidMax) return false;
      if (selectedHouses.size > 0 && !selectedHouses.has(auction.auctionHouseName)) return false;
      if (selectedBrand && auction.brand !== selectedBrand) return false;
      if (selectedLocation && auction.location !== selectedLocation) return false;
      if (selectedStatus && getStatus(auction) !== selectedStatus) return false;
      if (startFromDate && new Date(auction.startDate) < startFromDate) return false;
      if (endToDate && new Date(auction.endDate) > endToDate) return false;

      return true;
    });
  }, [
    normalizedQuery,
    bidMin,
    bidMax,
    selectedHouses,
    selectedBrand,
    selectedLocation,
    selectedStatus,
    startFrom,
    endTo,
  ]);

  const clearFilters = () => {
    setSearchQuery("");
    setBidRange([filterOptions.bidMin, filterOptions.bidMax]);
    setSelectedHouses(new Set());
    setSelectedBrand("");
    setSelectedLocation("");
    setSelectedStatus("");
    setStartFrom("");
    setEndTo("");
  };

  const totalLots = auctions.length;
  const totalHouses = new Set(auctions.map((auction) => auction.auctionHouseId)).size;
  const liveLots = auctions.filter((auction) => getStatus(auction) === "Live").length;
  const filteredCount = filteredAuctions.length;

  return (
    <div>
      <PageHeader title="Auctions" subtitle="Track live lots and upcoming closes from major houses" />

      <div className="grid gap-4 sm:grid-cols-3">
        <ContentCard className="flex flex-col gap-2 border border-border/60 bg-card/80">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Total Lots</span>
          <p className="text-2xl font-semibold text-foreground">{totalLots}</p>
          <span className="text-xs text-muted-foreground">Unordered lots across houses</span>
        </ContentCard>
        <ContentCard className="flex flex-col gap-2 border border-border/60 bg-card/80">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Auction Houses</span>
          <p className="text-2xl font-semibold text-foreground">{totalHouses}</p>
          <span className="text-xs text-muted-foreground">Global partners in this feed</span>
        </ContentCard>
        <ContentCard className="flex flex-col gap-2 border border-border/60 bg-card/80">
          <span className="text-xs uppercase tracking-[0.2em] text-muted-foreground">Live Right Now</span>
          <p className="text-2xl font-semibold text-foreground">{liveLots}</p>
          <span className="text-xs text-muted-foreground">Bidding currently open</span>
        </ContentCard>
      </div>

      <div className="mt-6 flex flex-col gap-6 lg:flex-row">
        <div className="flex-1 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-sm text-muted-foreground">
              {filteredCount} lots · {liveLots} live · {totalHouses} houses
            </p>
            <Button
              variant="outline"
              onClick={() => setFiltersOpen((open) => !open)}
              aria-expanded={filtersOpen}
              aria-controls="auctions-filters"
            >
              {filtersOpen ? <X className="h-4 w-4" /> : <Filter className="h-4 w-4" />}
              {filtersOpen ? "Hide filters" : "Show filters"}
            </Button>
          </div>

          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {filteredAuctions.map((auction) => {
              const status = getStatus(auction);
              const statusVariant = getStatusVariant(status);

              return (
                <ContentCard key={auction.id} className="flex h-full flex-col gap-4 border border-border/60">
                  <div className="flex flex-wrap items-start gap-4">
                    <div className="aspect-square w-1/2 min-w-[140px] flex-shrink-0 overflow-hidden rounded-[var(--radius-surface)] bg-muted">
                      <SolidPlaceholder className="h-full w-full rounded-[var(--radius-surface)]" />
                    </div>
                    <div className="flex flex-1 flex-col gap-2">
                      <div>
                        <p className="text-xs uppercase tracking-[0.2em] text-muted-foreground">{auction.brand}</p>
                        <h3 className="text-lg font-semibold text-foreground">{auction.model}</h3>
                        <p className="text-sm text-muted-foreground">Lot #{auction.lotNumber}</p>
                      </div>
                      <div>
                        <p className="text-lg font-semibold text-foreground">{formatCurrency(auction.currentBid)}</p>
                        <p className="text-xs text-muted-foreground">Current bid</p>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <Badge variant={statusVariant}>{status}</Badge>
                    <Badge variant="secondary">{auction.auctionHouseName}</Badge>
                  </div>

                  <div className="grid grid-cols-2 gap-0 overflow-hidden rounded-[var(--radius-surface)] border border-border/70 text-sm text-muted-foreground">
                    <div className="border-b border-r border-border/60 p-3">
                      <span className="font-medium text-foreground">Estimate</span>
                      <div>{auction.estimation}</div>
                    </div>
                    <div className="border-b border-border/60 p-3">
                      <span className="font-medium text-foreground">House ID</span>
                      <div>{auction.auctionHouseId}</div>
                    </div>
                    <div className="border-r border-border/60 p-3">
                      <span className="font-medium text-foreground">Starts</span>
                      <div>{auction.startDate}</div>
                    </div>
                    <div className="p-3">
                      <span className="font-medium text-foreground">Ends</span>
                      <div>{auction.endDate}</div>
                    </div>
                  </div>

                  <div className="mt-auto flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground">
                    <span className="inline-flex items-center gap-2">
                      <span aria-hidden>{getFlagEmoji(auction.location)}</span>
                      <span>{auction.location}</span>
                    </span>
                    <span>{auction.auctionHouseName}</span>
                  </div>
                </ContentCard>
              );
            })}
          </div>
        </div>

        {filtersOpen ? (
          <aside id="auctions-filters" className="w-full lg:w-[320px] lg:flex-shrink-0">
            <ContentCard className="sticky top-6 flex flex-col gap-6 border border-border/60 bg-card/90 p-5">
              <div>
                <p className="text-xs uppercase tracking-[0.25em] text-muted-foreground">Filters</p>
                <h2 className="text-lg font-semibold text-foreground">Refine lots</h2>
              </div>

              <div className="space-y-3">
                <label className="text-sm font-medium text-foreground" htmlFor="auctions-search">
                  Search
                </label>
                <Input
                  id="auctions-search"
                  placeholder="Brand, model, house, lot #"
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.target.value)}
                />
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-foreground">Current bid</span>
                  <span className="text-xs text-muted-foreground">
                    {formatCurrency(bidMin)} - {formatCurrency(bidMax)}
                  </span>
                </div>
                <Slider
                  value={[bidMin, bidMax]}
                  max={filterOptions.bidMax}
                  min={filterOptions.bidMin}
                  step={250}
                  onValueChange={(value) => setBidRange([value[0], value[1]])}
                />
                <div className="grid grid-cols-2 gap-3">
                  <Input
                    type="number"
                    placeholder="Min"
                    value={bidMin}
                    onChange={(event) => handleBidInput(0, event.target.value)}
                  />
                  <Input
                    type="number"
                    placeholder="Max"
                    value={bidMax}
                    onChange={(event) => handleBidInput(1, event.target.value)}
                  />
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Auction house</span>
                <div className="space-y-2">
                  {filterOptions.houses.map((house) => (
                    <label key={house} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Checkbox
                        checked={selectedHouses.has(house)}
                        onCheckedChange={() => toggleSetValue(setSelectedHouses, house)}
                      />
                      <span>{house}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Brand</span>
                <Select
                  value={selectedBrand || "any"}
                  onValueChange={(value) => setSelectedBrand(value === "any" ? "" : value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any brand" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any brand</SelectItem>
                    {filterOptions.brands.map((brand) => (
                      <SelectItem key={brand} value={brand}>
                        {brand}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
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
                <span className="text-sm font-medium text-foreground">Status</span>
                <Select
                  value={selectedStatus || "any"}
                  onValueChange={(value) => setSelectedStatus(value === "any" ? "" : value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Any status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="any">Any status</SelectItem>
                    <SelectItem value="Live">Live</SelectItem>
                    <SelectItem value="Upcoming">Upcoming</SelectItem>
                    <SelectItem value="Closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-3">
                <span className="text-sm font-medium text-foreground">Auction window</span>
                <div className="grid grid-cols-2 gap-3">
                  <Input type="date" value={startFrom} onChange={(event) => setStartFrom(event.target.value)} />
                  <Input type="date" value={endTo} onChange={(event) => setEndTo(event.target.value)} />
                </div>
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

export default Auctions;
