import brandsRaw from "@/fixtures/marketplace/brands.json";
import modelsRaw from "@/fixtures/marketplace/models.json";
import watchesRaw from "@/fixtures/marketplace/watches.json";
import materialsRaw from "@/fixtures/lookups/materials.json";
import dialColorsRaw from "@/fixtures/lookups/dial-colors.json";
import movementTypesRaw from "@/fixtures/lookups/movement-types.json";
import strapTypesRaw from "@/fixtures/lookups/strap-types.json";

export interface MarketBrand {
  id: string;
  name: string;
  country: string;
  foundedYear: number | null;
}

export interface MarketModel {
  id: string;
  brandId: string;
  name: string;
  collection: string | null;
  complication: string | null;
  caseShape: string | null;
  launchYear: number | null;
}

export interface MarketWatch {
  id: string;
  brandId: string;
  modelId: string;
  reference: string;
  marketValueUsd: number;
  currency: "USD";
  productionYear: number;
  caseSizeMm: number;
  caseMaterialId: string;
  dialColorId: string;
  movementTypeId: string;
  braceletTypeId: string;
  modelSequence: number;
}

export interface HydratedMarketWatch extends MarketWatch {
  brandName: string;
  modelName: string;
  collection: string;
  complication: string;
  caseShape: string;
  caseMaterial: string;
  dialColor: string;
  movementType: string;
  braceletType: string;
}

interface LookupValue {
  id: string;
  label: string;
}

export const marketBrands: MarketBrand[] = brandsRaw as MarketBrand[];
export const marketModels: MarketModel[] = modelsRaw as MarketModel[];
export const marketWatchesRaw: MarketWatch[] = watchesRaw as MarketWatch[];
export const materials: LookupValue[] = materialsRaw as LookupValue[];
export const dialColors: LookupValue[] = dialColorsRaw as LookupValue[];
export const movementTypes: LookupValue[] = movementTypesRaw as LookupValue[];
export const strapTypes: LookupValue[] = strapTypesRaw as LookupValue[];

const brandById = new Map(marketBrands.map((brand) => [brand.id, brand]));
const modelById = new Map(marketModels.map((model) => [model.id, model]));
const materialById = new Map(materials.map((material) => [material.id, material]));
const dialColorById = new Map(dialColors.map((dialColor) => [dialColor.id, dialColor]));
const movementTypeById = new Map(movementTypes.map((movementType) => [movementType.id, movementType]));
const strapTypeById = new Map(strapTypes.map((strapType) => [strapType.id, strapType]));

export const marketWatches: HydratedMarketWatch[] = marketWatchesRaw
  .map((watch) => {
    const brand = brandById.get(watch.brandId);
    const model = modelById.get(watch.modelId);
    const material = materialById.get(watch.caseMaterialId);
    const dialColor = dialColorById.get(watch.dialColorId);
    const movementType = movementTypeById.get(watch.movementTypeId);
    const strapType = strapTypeById.get(watch.braceletTypeId);

    if (!brand || !model || !material || !dialColor || !movementType || !strapType) return null;

    return {
      ...watch,
      brandName: brand.name,
      modelName: model.name,
      collection: model.collection ?? "N/A",
      complication: model.complication ?? "N/A",
      caseShape: model.caseShape ?? "N/A",
      caseMaterial: material.label,
      dialColor: dialColor.label,
      movementType: movementType.label,
      braceletType: strapType.label,
    };
  })
  .filter((watch): watch is HydratedMarketWatch => watch !== null)
  .sort((a, b) => b.marketValueUsd - a.marketValueUsd);

export const marketDataHealth = {
  watchesWithMissingBrand: marketWatchesRaw.filter((watch) => !brandById.has(watch.brandId)).map((watch) => watch.id),
  watchesWithMissingModel: marketWatchesRaw.filter((watch) => !modelById.has(watch.modelId)).map((watch) => watch.id),
  watchesWithMissingMaterial: marketWatchesRaw
    .filter((watch) => !materialById.has(watch.caseMaterialId))
    .map((watch) => watch.id),
  watchesWithMissingDialColor: marketWatchesRaw
    .filter((watch) => !dialColorById.has(watch.dialColorId))
    .map((watch) => watch.id),
  watchesWithMissingMovementType: marketWatchesRaw
    .filter((watch) => !movementTypeById.has(watch.movementTypeId))
    .map((watch) => watch.id),
  watchesWithMissingBraceletType: marketWatchesRaw
    .filter((watch) => !strapTypeById.has(watch.braceletTypeId))
    .map((watch) => watch.id),
};
