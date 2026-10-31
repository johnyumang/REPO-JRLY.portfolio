// JRLY store seed: store settings, region, shipping, publishable key, and the storefront's own
// 48-product catalogue (content/catalog.ts, mirrored to src/data/catalog.ts), so the offline storefront and Medusa never disagree.
// Run once on an empty, migrated database: npm run seed
import { CreateInventoryLevelInput, ExecArgs } from "@medusajs/framework/types";
import { ContainerRegistrationKeys, Modules, ProductStatus } from "@medusajs/framework/utils";
import {
  createApiKeysWorkflow,
  createInventoryLevelsWorkflow,
  createProductCategoriesWorkflow,
  createProductsWorkflow,
  createRegionsWorkflow,
  createSalesChannelsWorkflow,
  createShippingOptionsWorkflow,
  createShippingProfilesWorkflow,
  createStockLocationsWorkflow,
  createTaxRegionsWorkflow,
  linkSalesChannelsToApiKeyWorkflow,
  linkSalesChannelsToStockLocationWorkflow,
  updateStoresWorkflow,
} from "@medusajs/medusa/core-flows";
import { collections, products, variantsOf } from "../data/catalog";

const STORE_NAME = process.env.STORE_NAME || "JRLY";
const STOREFRONT_URL = (process.env.STOREFRONT_URL || "http://localhost:3000").replace(/\/$/, "");
// Where product photos live. In the Docker image they are bundled and served by Medusa at /static/stock,
// so on Render (which sets RENDER_EXTERNAL_URL) images work without the storefront being online.
const IMAGE_BASE = (
  process.env.IMAGE_BASE_URL ||
  (process.env.RENDER_EXTERNAL_URL ? `${process.env.RENDER_EXTERNAL_URL}/static/stock` : `${STOREFRONT_URL}/stock`)
).replace(/\/$/, "");
const COUNTRIES = ["de", "fr", "es", "it", "nl", "be", "at", "ie", "pt"];
const CURRENCY = "eur"; // matches the storefront's € prices
const SHIPPING = { standard: 4.95, express: 9.95, freeOver: 50 }; // same rule as content/seed.ts

export default async function seedJrly({ container }: ExecArgs) {
  const logger = container.resolve(ContainerRegistrationKeys.LOGGER);
  const link = container.resolve(ContainerRegistrationKeys.LINK);
  const query = container.resolve(ContainerRegistrationKeys.QUERY);
  const fulfillment = container.resolve(Modules.FULFILLMENT);
  const salesChannels = container.resolve(Modules.SALES_CHANNEL);
  const stores = container.resolve(Modules.STORE);

  const [store] = await stores.listStores();
  if (store.metadata?.jrly_seeded) {
    logger.info(`${STORE_NAME} is already seeded. Nothing to do.`);
    return;
  }

  logger.info(`Seeding ${STORE_NAME} store settings...`);
  let [channel] = await salesChannels.listSalesChannels({ name: "Webshop" });
  if (!channel) {
    const { result } = await createSalesChannelsWorkflow(container).run({
      input: { salesChannelsData: [{ name: "Webshop", description: `${STORE_NAME} storefront` }] },
    });
    channel = result[0];
  }
  await updateStoresWorkflow(container).run({
    input: {
      selector: { id: store.id },
      update: {
        name: STORE_NAME,
        supported_currencies: [{ currency_code: CURRENCY, is_default: true }],
        default_sales_channel_id: channel.id,
      },
    },
  });

  const { result: [region] } = await createRegionsWorkflow(container).run({
    input: { regions: [{ name: "Europe", currency_code: CURRENCY, countries: COUNTRIES, payment_providers: ["pp_system_default"] }] },
  });
  await createTaxRegionsWorkflow(container).run({
    input: COUNTRIES.map((country_code) => ({ country_code, provider_id: "tp_system" })),
  });

  const { result: [location] } = await createStockLocationsWorkflow(container).run({
    input: { locations: [{ name: `${STORE_NAME} Warehouse`, address: { city: "[CITY]", country_code: "DE", address_1: "[ADDRESS]" } }] },
  });
  await updateStoresWorkflow(container).run({ input: { selector: { id: store.id }, update: { default_location_id: location.id } } });
  await link.create({
    [Modules.STOCK_LOCATION]: { stock_location_id: location.id },
    [Modules.FULFILLMENT]: { fulfillment_provider_id: "manual_manual" },
  });

  logger.info("Seeding shipping...");
  let [profile] = await fulfillment.listShippingProfiles({ type: "default" });
  if (!profile) {
    const { result } = await createShippingProfilesWorkflow(container).run({
      input: { data: [{ name: "Default Shipping Profile", type: "default" }] },
    });
    profile = result[0];
  }
  const fulfillmentSet = await fulfillment.createFulfillmentSets({
    name: `${STORE_NAME} delivery`,
    type: "shipping",
    service_zones: [{ name: "Europe", geo_zones: COUNTRIES.map((country_code) => ({ country_code, type: "country" as const })) }],
  });
  await link.create({
    [Modules.STOCK_LOCATION]: { stock_location_id: location.id },
    [Modules.FULFILLMENT]: { fulfillment_set_id: fulfillmentSet.id },
  });
  const storeRules = [
    { attribute: "enabled_in_store", value: "true", operator: "eq" as const },
    { attribute: "is_return", value: "false", operator: "eq" as const },
  ];
  await createShippingOptionsWorkflow(container).run({
    input: [
      {
        name: "Standard Shipping",
        price_type: "flat",
        provider_id: "manual_manual",
        service_zone_id: fulfillmentSet.service_zones[0].id,
        shipping_profile_id: profile.id,
        type: { label: "Standard", description: `2–4 business days. Free over €${SHIPPING.freeOver}.`, code: "standard" },
        prices: [
          { currency_code: CURRENCY, amount: SHIPPING.standard },
          { region_id: region.id, amount: SHIPPING.standard },
          // Free standard shipping once the cart reaches the threshold
          { region_id: region.id, amount: 0, rules: [{ attribute: "item_total", operator: "gte", value: SHIPPING.freeOver }] },
        ],
        rules: storeRules,
      },
      {
        name: "Express Shipping",
        price_type: "flat",
        provider_id: "manual_manual",
        service_zone_id: fulfillmentSet.service_zones[0].id,
        shipping_profile_id: profile.id,
        type: { label: "Express", description: "Next business day.", code: "express" },
        prices: [
          { currency_code: CURRENCY, amount: SHIPPING.express },
          { region_id: region.id, amount: SHIPPING.express },
        ],
        rules: storeRules,
      },
    ],
  });
  await linkSalesChannelsToStockLocationWorkflow(container).run({ input: { id: location.id, add: [channel.id] } });

  logger.info("Seeding publishable API key...");
  const { result: [apiKey] } = await createApiKeysWorkflow(container).run({
    input: { api_keys: [{ title: `${STORE_NAME} storefront`, type: "publishable", created_by: "" }] },
  });
  await linkSalesChannelsToApiKeyWorkflow(container).run({ input: { id: apiKey.id, add: [channel.id] } });

  logger.info(`Seeding ${collections.length} categories and ${products.length} products...`);
  const { result: categories } = await createProductCategoriesWorkflow(container).run({
    input: { product_categories: collections.map((c) => ({ name: c.title, handle: c.slug, is_active: true })) },
  });
  const categoryId = Object.fromEntries(categories.map((c) => [c.handle, c.id]));

  const stockBySku = new Map<string, number>();
  await createProductsWorkflow(container).run({
    input: {
      products: products.map((p) => {
        const variants = variantsOf(p);
        variants.forEach((v) => stockBySku.set(v.sku, v.stock));
        return {
          title: p.name,
          handle: p.slug,
          description: p.description,
          material: p.composition,
          status: ProductStatus.PUBLISHED,
          shipping_profile_id: profile.id,
          category_ids: p.collections.map((c) => categoryId[c]).filter(Boolean),
          thumbnail: `${IMAGE_BASE}/${p.images[0]}-800.webp`,
          images: p.images.map((img) => ({ url: `${IMAGE_BASE}/${img}-1400.webp` })),
          metadata: { badge: p.badge ?? null, compare_at: p.compareAt ?? null, colors: p.colors, created_at: p.createdAt },
          options: [
            { title: "Color", values: p.colors.map((c) => c.name) },
            { title: "Size", values: p.sizes },
          ],
          variants: variants.map((v) => ({
            title: `${v.color} / ${v.size}`,
            sku: v.sku,
            manage_inventory: true,
            options: { Color: v.color, Size: v.size },
            prices: [{ currency_code: CURRENCY, amount: p.price }],
          })),
          sales_channels: [{ id: channel.id }],
        };
      }),
    },
  });

  logger.info("Seeding inventory levels...");
  const { data: items } = await query.graph({ entity: "inventory_item", fields: ["id", "sku"] });
  const levels: CreateInventoryLevelInput[] = items.map((item) => ({
    location_id: location.id,
    inventory_item_id: item.id,
    stocked_quantity: stockBySku.get(item.sku ?? "") ?? 0,
  }));
  await createInventoryLevelsWorkflow(container).run({ input: { inventory_levels: levels } });

  await updateStoresWorkflow(container).run({
    input: { selector: { id: store.id }, update: { metadata: { jrly_seeded: new Date().toISOString() } } },
  });

  logger.info(`Done. Publishable key for the storefront (NEXT_PUBLIC_MEDUSA_PUBLISHABLE_KEY): ${apiKey.token}`);
}
