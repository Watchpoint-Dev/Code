import insightsRaw from "@/fixtures/watch-insights/insights.json";
import { watches, type TopPerformerWatch } from "@/lib/dummy-data";

interface WatchInsightRaw {
  watchId: string;
  retailPriceUsd: number;
  performanceIndex: number;
  activeListings: number;
  waterResistanceM: number;
  caliber: string;
  crystal: string;
  powerReserveHours: number;
}

export interface WatchInsight extends TopPerformerWatch {
  retailPriceUsd: number;
  performanceIndex: number;
  activeListings: number;
  waterResistanceM: number;
  caliber: string;
  crystal: string;
  powerReserveHours: number;
  complication: string;
}

const insightsDataset = insightsRaw as WatchInsightRaw[];
const insightByWatchId = new Map(insightsDataset.map((item) => [item.watchId, item]));

const complicationBySegment: Record<string, string> = {
  Diver: "Date",
  Travel: "GMT",
  Sports: "Chronograph",
  Chronograph: "Chronograph",
  Dress: "Small Seconds",
  Complications: "Annual Calendar",
};

const buildFallbackInsight = (watch: TopPerformerWatch): Omit<WatchInsight, keyof TopPerformerWatch> => {
  const retailPriceUsd = Math.round(watch.marketPrice * 0.68);
  const performanceIndex = Number(((watch.performance["1y"] + watch.performance["6m"]) / 6).toFixed(2));

  return {
    retailPriceUsd,
    performanceIndex,
    activeListings: 1,
    waterResistanceM: watch.segment === "Diver" ? 300 : 100,
    caliber: `CAL-${watch.reference}`,
    crystal: "Sapphire",
    powerReserveHours: watch.movement === "Automatic" ? 70 : watch.movement === "Manual" ? 48 : 40,
    complication: complicationBySegment[watch.segment] ?? "Time Only",
  };
};

export const watchInsights: WatchInsight[] = watches.map((watch) => {
  const insight = insightByWatchId.get(watch.id);
  const fallback = buildFallbackInsight(watch);
  const complication = fallback.complication;

  return {
    ...watch,
    retailPriceUsd: insight?.retailPriceUsd ?? fallback.retailPriceUsd,
    performanceIndex: insight?.performanceIndex ?? fallback.performanceIndex,
    activeListings: insight?.activeListings ?? fallback.activeListings,
    waterResistanceM: insight?.waterResistanceM ?? fallback.waterResistanceM,
    caliber: insight?.caliber ?? fallback.caliber,
    crystal: insight?.crystal ?? fallback.crystal,
    powerReserveHours: insight?.powerReserveHours ?? fallback.powerReserveHours,
    complication,
  };
});

export const watchInsightById = new Map(watchInsights.map((watch) => [watch.id, watch]));
