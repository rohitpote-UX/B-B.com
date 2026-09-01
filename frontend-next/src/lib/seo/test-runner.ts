/**
 * Brand Battle — Frontend SEO & Schema.org Automated Validation Suite
 * Executes programmatic checks across all lib/seo generators.
 */

import {
  buildProductTitle,
  buildComparisonTitle,
  buildProductDescription,
  buildComparisonDescription,
  buildProductCanonical,
  buildComparisonCanonical,
  sanitizeCanonicalUrl,
  buildComparisonSlug,
  buildRobotsDirectives,
  shouldNoindexQuery,
  evaluateSeoEligibility,
  SeoEligibilityStatus,
  isComparisonEligible,
  buildProductSchema,
  buildBreadcrumbSchema,
  buildOrganizationSchema,
  buildWebSiteSchema,
  buildComparisonSchema,
  buildGeoFactSheet,
  buildProductAeoAnswers,
  buildComparisonAeoVerdict,
  buildProductImageAlt,
  validatePageSeo,
} from './index'

export function runSeoValidationSuite(): { passed: number; failed: number; results: string[] } {
  const results: string[] = []
  let passed = 0
  let failed = 0

  function assert(condition: boolean, testName: string) {
    if (condition) {
      passed++
      results.push(`✅ PASS: ${testName}`)
    } else {
      failed++
      results.push(`❌ FAIL: ${testName}`)
    }
  }

  // 1. Title Generator Tests
  const pTitle = buildProductTitle({ name: 'Apple AirPods Pro 2', brand: 'Apple' })
  assert(pTitle.includes('AirPods Pro 2') && pTitle.includes('Brand Battle'), 'Product title generation')
  assert(pTitle.length <= 60, 'Product title length <= 60 chars')

  const cTitle = buildComparisonTitle({ product1Name: 'iPhone 16', product2Name: 'Galaxy S25' })
  assert(cTitle.includes('iPhone 16 vs Galaxy S25'), 'Comparison title generation')
  assert(cTitle.length <= 60, 'Comparison title length <= 60 chars')

  // 2. Meta Description Tests
  const pDesc = buildProductDescription({
    name: 'AirPods Pro 2',
    brand: 'Apple',
    category: 'Audio',
    price: 18999,
  })
  assert(pDesc.includes('18,999') && pDesc.includes('AirPods Pro 2'), 'Product meta description includes price and name')
  assert(pDesc.length <= 160, 'Product description length <= 160 chars')

  const cDesc = buildComparisonDescription({
    product1Name: 'iPhone 16',
    product2Name: 'Galaxy S25',
    price1: 79900,
    price2: 74999,
  })
  assert(cDesc.includes('79,900') && cDesc.includes('74,999'), 'Comparison description contains both prices')

  // 3. Canonical URL System Tests
  const pCanonical = buildProductCanonical(10)
  assert(pCanonical === 'https://brandbattle.com/product/10', 'Product canonical URL')

  const cCanonical = buildComparisonCanonical('iphone-16-vs-galaxy-s25')
  assert(cCanonical === 'https://brandbattle.com/compare/iphone-16-vs-galaxy-s25', 'Comparison canonical URL')

  const cleanUrl = sanitizeCanonicalUrl('https://brandbattle.com/compare/a-vs-b?utm_source=google&sort=price')
  assert(!cleanUrl.includes('utm_source') && !cleanUrl.includes('sort'), 'Sanitize canonical URL strips tracking/sort params')

  const compSlug = buildComparisonSlug('iPhone 17 Pro Max', 'Samsung Galaxy S26 Ultra')
  assert(compSlug === 'iphone-17-pro-max-vs-samsung-galaxy-s26-ultra', 'Comparison slug formatting')

  // 4. Indexability & Thin Content Protection Tests
  const validMetrics = {
    id: 1,
    name: 'Sony WH-1000XM5',
    hasBrand: true,
    hasCategory: true,
    hasValidImage: true,
    hasVerifiedPrice: true,
    hasSpecs: true,
    descriptionLength: 120,
  }
  assert(evaluateSeoEligibility(validMetrics) === SeoEligibilityStatus.SEO_ELIGIBLE, 'Valid product is SEO_ELIGIBLE')

  const thinMetrics = {
    id: 2,
    name: 'A',
    hasBrand: false,
    hasCategory: false,
    hasValidImage: false,
    hasVerifiedPrice: false,
    hasSpecs: false,
    descriptionLength: 5,
  }
  assert(evaluateSeoEligibility(thinMetrics) === SeoEligibilityStatus.SEO_LOW_QUALITY, 'Thin product is SEO_LOW_QUALITY')

  assert(isComparisonEligible(validMetrics, validMetrics, 'Audio', 'Audio') === false, 'Same product ID cannot form comparison')

  // 5. Robots Directives Tests
  const robotsIndex = buildRobotsDirectives({ isIndexable: true })
  assert(Boolean(robotsIndex && typeof robotsIndex === 'object' && robotsIndex.index === true && robotsIndex.follow === true), 'Robots allows indexable page')

  const shouldNoindex = shouldNoindexQuery({ sort: 'price_asc', color: 'blue' })
  assert(shouldNoindex === true, 'Faceted query params trigger noindex')

  // 6. Schema.org Product JSON-LD Tests
  const pSchema = buildProductSchema({
    id: 1,
    name: 'Apple AirPods Pro 2',
    brand: 'Apple',
    category: 'Audio',
    price: 18999,
    url: 'https://brandbattle.com/product/1',
  })
  assert(pSchema['@type'] === 'Product', 'Product schema @type is Product')
  const offer = pSchema.offers as Record<string, unknown> | undefined
  assert(offer?.price === 18999, 'Product schema offers price is accurate')
  assert(pSchema.aggregateRating === undefined, 'No fake ratings when totalReviews is 0/undefined')

  // 7. Schema.org Breadcrumb & WebSite & Organization Tests
  const breadcrumbSchema = buildBreadcrumbSchema([
    { name: 'Home', url: 'https://brandbattle.com' },
    { name: 'Audio', url: 'https://brandbattle.com/discover?category=audio' },
  ])
  assert(breadcrumbSchema['@type'] === 'BreadcrumbList', 'BreadcrumbList schema type')

  const orgSchema = buildOrganizationSchema()
  assert(orgSchema['@type'] === 'Organization', 'Organization schema type')

  const siteSchema = buildWebSiteSchema()
  assert(siteSchema['@type'] === 'WebSite', 'WebSite schema type')

  // 8. Schema.org Comparison Graph Tests
  const compGraph = buildComparisonSchema({
    product1: { id: 1, name: 'Prod A', price: 100, url: 'https://brandbattle.com/product/1' },
    product2: { id: 2, name: 'Prod B', price: 200, url: 'https://brandbattle.com/product/2' },
    canonicalUrl: 'https://brandbattle.com/compare/prod-a-vs-prod-b',
    breadcrumbs: [{ name: 'Home', url: 'https://brandbattle.com' }],
    faqs: [{ question: 'Which is cheaper?', answer: 'Prod A is cheaper.' }],
  })
  const graphNodes = (compGraph as Record<string, unknown>)['@graph']
  assert(Array.isArray(graphNodes), 'Comparison graph has @graph nodes')

  // 9. GEO & AEO Tests
  const geoSheet = buildGeoFactSheet({
    name: 'Sony WH-1000XM5',
    brand: 'Sony',
    category: 'Headphones',
    price: 24990,
  })
  assert(geoSheet.entityName === 'Sony WH-1000XM5' && geoSheet.verifiedPrice === 24990, 'GEO FactSheet generation')

  const aeoAnswers = buildProductAeoAnswers({
    name: 'AirPods Pro 2',
    brand: 'Apple',
    price: 18999,
    bestPlatform: 'Amazon',
    category: 'Audio',
  })
  assert(aeoAnswers.length >= 2, 'AEO answers generated')

  const aeoVerdict = buildComparisonAeoVerdict({
    p1Name: 'iPhone 16',
    p2Name: 'Galaxy S25',
    p1Price: 79900,
    p2Price: 74999,
    category: 'Smartphones',
    winnerName: 'Galaxy S25',
  })
  assert(aeoVerdict.directAnswer.includes('Galaxy S25'), 'AEO comparison verdict')

  // 10. Image SEO Test
  const altText = buildProductImageAlt({ productName: 'AirPods Pro 2', brand: 'Apple', category: 'Earbuds' })
  assert(altText.includes('Apple') && altText.includes('AirPods Pro 2'), 'Image ALT text generation')

  // 11. Automated Validator Test
  const validation = validatePageSeo({
    title: 'Apple AirPods Pro 2 — Price, Features & Specs | Brand Battle',
    description: 'Compare Apple AirPods Pro 2 in Audio. Starting from ₹18,999. Track price history and AI insights on Brand Battle.',
    canonicalUrl: 'https://brandbattle.com/product/1',
    jsonLd: pSchema,
  })
  assert(validation.isValid === true && validation.score >= 90, 'Page validation score >= 90')

  return { passed, failed, results }
}
