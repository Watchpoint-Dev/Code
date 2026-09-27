import brandsRaw from "@/fixtures/marketplace/brands.json";
import modelsRaw from "@/fixtures/marketplace/models.json";
import watchesRaw from "@/fixtures/watches/watches.json";
import marketplaceListingsRaw from "@/fixtures/marketplace/listings.json";
import segmentsRaw from "@/fixtures/lookups/segments.json";
import materialsRaw from "@/fixtures/lookups/materials.json";
import dialColorsRaw from "@/fixtures/lookups/dial-colors.json";
import movementTypesRaw from "@/fixtures/lookups/movement-types.json";
import strapTypesRaw from "@/fixtures/lookups/strap-types.json";
import conditionsRaw from "@/fixtures/lookups/conditions.json";
import availabilityStatusesRaw from "@/fixtures/lookups/availability-statuses.json";
import sellersRaw from "@/fixtures/lookups/sellers.json";
import locationsRaw from "@/fixtures/lookups/locations.json";

interface Brand {
  id: string;
  name: string;
}

interface Model {
  id: string;
  brandId: string;
  name: string;
}

interface Lookup {
  id: string;
  label: string;
}

interface TopPerformerWatchRaw {
  id: string;
  brandId: string;
  modelId: string;
  reference: string;
  segmentId: string;
  year: number;
  caseSizeMm: number;
  materialId: string;
  dialColorId: string;
  movementTypeId: string;
  marketPrice: number;
  currency: string;
  performance: {
    "3m": number;
    "6m": number;
    "1y": number;
    "2y": number;
  };
}

interface MarketplaceListingRaw {
  id: string;
  brandId: string;
  modelId: string;
  reference: string;
  price: number;
  currency: string;
  conditionId: string;
  year: number;
  caseSizeMm: number;
  materialId: string;
  movementTypeId: string;
  dialColorId: string;
  strapTypeId: string;
  locationId: string;
  availabilityId: string;
  sellerId: string;
  description: string;
  tags: string[];
  featured: boolean;
}

export interface TopPerformerWatch extends TopPerformerWatchRaw {
  brand: string;
  model: string;
  segment: string;
  material: string;
  dial: string;
  movement: string;
}

export interface MarketplaceListing extends MarketplaceListingRaw {
  brand: string;
  model: string;
  condition: string;
  material: string;
  movement: string;
  dial: string;
  strap: string;
  location: string;
  availability: string;
  seller: string;
}

const brands = brandsRaw as Brand[];
const models = modelsRaw as Model[];
const watchesDataset = watchesRaw as TopPerformerWatchRaw[];
const marketplaceListingsDataset = marketplaceListingsRaw as MarketplaceListingRaw[];
const segments = segmentsRaw as Lookup[];
const materials = materialsRaw as Lookup[];
const dialColors = dialColorsRaw as Lookup[];
const movementTypes = movementTypesRaw as Lookup[];
const strapTypes = strapTypesRaw as Lookup[];
const conditions = conditionsRaw as Lookup[];
const availabilityStatuses = availabilityStatusesRaw as Lookup[];
const sellers = sellersRaw as Lookup[];
const locations = locationsRaw as Lookup[];

const brandById = new Map(brands.map((brand) => [brand.id, brand]));
const modelById = new Map(models.map((model) => [model.id, model]));
const segmentById = new Map(segments.map((segment) => [segment.id, segment]));
const materialById = new Map(materials.map((material) => [material.id, material]));
const dialColorById = new Map(dialColors.map((dial) => [dial.id, dial]));
const movementTypeById = new Map(movementTypes.map((movement) => [movement.id, movement]));
const strapTypeById = new Map(strapTypes.map((strap) => [strap.id, strap]));
const conditionById = new Map(conditions.map((condition) => [condition.id, condition]));
const availabilityById = new Map(availabilityStatuses.map((status) => [status.id, status]));
const sellerById = new Map(sellers.map((seller) => [seller.id, seller]));
const locationById = new Map(locations.map((location) => [location.id, location]));

export const watches: TopPerformerWatch[] = watchesDataset
  .map((watch) => {
    const brand = brandById.get(watch.brandId);
    const model = modelById.get(watch.modelId);
    const segment = segmentById.get(watch.segmentId);
    const material = materialById.get(watch.materialId);
    const dial = dialColorById.get(watch.dialColorId);
    const movement = movementTypeById.get(watch.movementTypeId);

    if (!brand || !model || !segment || !material || !dial || !movement) return null;

    return {
      ...watch,
      brand: brand.name,
      model: model.name,
      segment: segment.label,
      material: material.label,
      dial: dial.label,
      movement: movement.label,
    };
  })
  .filter((watch): watch is TopPerformerWatch => watch !== null);

export const topPerformerWatches = watches;

export const marketplaceListings: MarketplaceListing[] = marketplaceListingsDataset
  .map((listing) => {
    const brand = brandById.get(listing.brandId);
    const model = modelById.get(listing.modelId);
    const condition = conditionById.get(listing.conditionId);
    const material = materialById.get(listing.materialId);
    const movement = movementTypeById.get(listing.movementTypeId);
    const dial = dialColorById.get(listing.dialColorId);
    const strap = strapTypeById.get(listing.strapTypeId);
    const location = locationById.get(listing.locationId);
    const availability = availabilityById.get(listing.availabilityId);
    const seller = sellerById.get(listing.sellerId);

    if (!brand || !model || !condition || !material || !movement || !dial || !strap || !location || !availability || !seller) {
      return null;
    }

    return {
      ...listing,
      brand: brand.name,
      model: model.name,
      condition: condition.label,
      material: material.label,
      movement: movement.label,
      dial: dial.label,
      strap: strap.label,
      location: location.label,
      availability: availability.label,
      seller: seller.label,
    };
  })
  .filter((listing): listing is MarketplaceListing => listing !== null);

export const dummyDataHealth = {
  watchesWithMissingBrand: watchesDataset
    .filter((watch) => !brandById.has(watch.brandId))
    .map((watch) => watch.id),
  watchesWithMissingModel: watchesDataset
    .filter((watch) => !modelById.has(watch.modelId))
    .map((watch) => watch.id),
  marketplaceListingsWithMissingBrand: marketplaceListingsDataset
    .filter((listing) => !brandById.has(listing.brandId))
    .map((listing) => listing.id),
  marketplaceListingsWithMissingModel: marketplaceListingsDataset
    .filter((listing) => !modelById.has(listing.modelId))
    .map((listing) => listing.id),
};
