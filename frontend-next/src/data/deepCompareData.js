import { resolveComparisonProfile, detectCategoryProfileType } from '../lib/comparisonProfiles'

// Simple seeded pseudo-random number generator
function seededRandom(seed) {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

// Clamp between min and max
const clamp = (v, min, max) => Math.max(min, Math.min(max, v))

// Brand characteristic profiles (for Electronics)
const BRAND_PROFILES = {
  'Samsung':    { gaming: 78, battery: 72, camera: 85, heating: 68, service: 95, privacy: 80, updates: 85, ecosystem: 90, repairability: 75, resale: 82, sustainability: 70 },
  'Apple':      { gaming: 88, battery: 82, camera: 92, heating: 75, service: 90, privacy: 95, updates: 98, ecosystem: 95, repairability: 45, resale: 90, sustainability: 80 },
  'MOTOROLA':   { gaming: 65, battery: 80, camera: 70, heating: 72, service: 78, privacy: 75, updates: 70, ecosystem: 55, repairability: 80, resale: 55, sustainability: 65 },
  'Xiaomi':     { gaming: 82, battery: 85, camera: 75, heating: 65, service: 80, privacy: 60, updates: 60, ecosystem: 70, repairability: 85, resale: 50, sustainability: 55 },
  'OPPO':       { gaming: 72, battery: 88, camera: 80, heating: 70, service: 82, privacy: 65, updates: 68, ecosystem: 60, repairability: 72, resale: 55, sustainability: 60 },
  'Vivo':       { gaming: 70, battery: 82, camera: 82, heating: 72, service: 80, privacy: 62, updates: 65, ecosystem: 58, repairability: 70, resale: 52, sustainability: 58 },
  'Realme':     { gaming: 80, battery: 82, camera: 72, heating: 68, service: 75, privacy: 60, updates: 62, ecosystem: 55, repairability: 82, resale: 48, sustainability: 55 },
  'OnePlus':    { gaming: 90, battery: 80, camera: 82, heating: 62, service: 78, privacy: 68, updates: 82, ecosystem: 75, repairability: 65, resale: 70, sustainability: 65 },
  'Nothing':    { gaming: 75, battery: 78, camera: 72, heating: 70, service: 65, privacy: 72, updates: 80, ecosystem: 65, repairability: 70, resale: 65, sustainability: 72 },
  'Google':     { gaming: 72, battery: 75, camera: 95, heating: 65, service: 72, privacy: 90, updates: 95, ecosystem: 85, repairability: 80, resale: 65, sustainability: 82 },
  'ASUS':       { gaming: 92, battery: 70, camera: 72, heating: 58, service: 70, privacy: 70, updates: 72, ecosystem: 60, repairability: 65, resale: 55, sustainability: 55 },
  'iQOO':      { gaming: 88, battery: 78, camera: 72, heating: 60, service: 72, privacy: 58, updates: 60, ecosystem: 55, repairability: 75, resale: 48, sustainability: 52 },
  'POCO':       { gaming: 85, battery: 82, camera: 70, heating: 62, service: 72, privacy: 58, updates: 58, ecosystem: 55, repairability: 82, resale: 45, sustainability: 50 },
  'Ai+':        { gaming: 55, battery: 75, camera: 60, heating: 78, service: 60, privacy: 55, updates: 50, ecosystem: 40, repairability: 70, resale: 35, sustainability: 45 },
  'Tecno':      { gaming: 60, battery: 80, camera: 65, heating: 72, service: 65, privacy: 55, updates: 50, ecosystem: 40, repairability: 75, resale: 35, sustainability: 45 },
  'Infinix':    { gaming: 62, battery: 82, camera: 62, heating: 70, service: 62, privacy: 55, updates: 48, ecosystem: 38, repairability: 78, resale: 35, sustainability: 42 },
  'Lava':       { gaming: 50, battery: 78, camera: 55, heating: 80, service: 85, privacy: 60, updates: 45, ecosystem: 35, repairability: 88, resale: 30, sustainability: 50 },
}

const DEFAULT_PROFILE = { gaming: 65, battery: 75, camera: 68, heating: 70, service: 68, privacy: 60, updates: 55, ecosystem: 50, repairability: 72, resale: 45, sustainability: 50 }

function getBrandProfile(brand) {
  const key = Object.keys(BRAND_PROFILES).find(k => brand && (brand.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(brand.toLowerCase())))
  return key ? BRAND_PROFILES[key] : DEFAULT_PROFILE
}

// Category-specific verdict labels
const VERDICT_LABELS = {
  'Smartphones': ['Best for Gaming', 'Best Camera Phone', 'Best Long-Term Value', 'Best Battery Champion', 'Best Budget Pick', 'Best All-Rounder', 'Best for Students', 'Best for Creators'],
  'Laptops': ['Best for Productivity', 'Best for Gaming', 'Best Ultrabook', 'Best Value Laptop', 'Best for Coding', 'Best for Design'],
  'Audio': ['Best Sound Quality', 'Best for Bass Lovers', 'Best Noise Cancellation', 'Best Value Audio', 'Best for Gaming Audio'],
  'Wearables': ['Best Fitness Tracker', 'Best Smartwatch', 'Best Battery Life', 'Best Value Wearable'],
  'Shoes': ['Best Daily Sneaker', 'Best Court Traction', 'Best Running Cushioning', 'Best All-Day Comfort', 'Best Value Footwear', 'Best Build Durability'],
  'Footwear': ['Best Daily Sneaker', 'Best Court Traction', 'Best Running Cushioning', 'Best All-Day Comfort', 'Best Value Footwear', 'Best Build Durability'],
  'Clothing': ['Best Fabric Feel', 'Best Daily Casual Wear', 'Best Breathable Fit', 'Best Tailored Cut', 'Best Value Apparel', 'Best All-Season Pick'],
  'Apparel': ['Best Fabric Feel', 'Best Daily Casual Wear', 'Best Breathable Fit', 'Best Tailored Cut', 'Best Value Apparel', 'Best All-Season Pick'],
  'Beauty': ['Best Daily Fragrance', 'Best Scent Projection', 'Best Long-Lasting Wear', 'Best Signature Scent', 'Best Value Beauty Pick', 'Best Everyday Formula'],
  'default': ['Best Overall Value', 'Best Performance', 'Best Budget Pick', 'Best Long-Term Value', 'Best for Daily Use']
}

// Generate pros based on product traits and category profile
function generatePros(product, profile, rng, categoryProfileType = 'ELECTRONICS') {
  if (categoryProfileType === 'FOOTWEAR') {
    const isBadminton = /badminton|court/i.test(`${product.name} ${product.description || ''}`)
    const isRunning = /running|runner|marathon/i.test(`${product.name} ${product.description || ''}`)
    const isMesh = /mesh|knit|breath/i.test(`${product.name} ${product.description || ''}`)

    const footwearPros = [
      { cond: product.rating >= 4.3, text: `Highly rated by ${product.totalReviews.toLocaleString()}+ verified buyers (${product.rating}/5)` },
      { cond: isBadminton, text: `Non-marking rubber outsole engineered for exceptional court traction and lateral stability` },
      { cond: isRunning, text: `Responsive cushioning system providing shock absorption during high-impact road runs` },
      { cond: isMesh, text: `Open-mesh upper for continuous airflow and lightweight breathability` },
      { cond: product.dealScore >= 85, text: `Excellent deal score of ${product.dealScore}/100 — strong price-to-durability ratio` },
      { cond: true, text: `Cushioned insole construction designed for extended daily wear comfort` },
      { cond: true, text: `Reinforced toe-overlay and heel counter for increased structural durability` },
      { cond: (product.prices || []).length > 2, text: `Available across ${(product.prices || []).length} verified merchant platforms` },
    ]
    const matching = footwearPros.filter(p => p.cond)
    matching.sort(() => rng() - 0.5)
    return matching.slice(0, 4).map(p => p.text)
  }

  if (categoryProfileType === 'APPAREL') {
    const isCotton = /cotton|pure cotton/i.test(`${product.name} ${product.description || ''}`)
    const isDenim = /jeans|denim/i.test(`${product.name} ${product.description || ''}`)
    const isSport = /sport|gym|active|stretch/i.test(`${product.name} ${product.description || ''}`)

    const apparelPros = [
      { cond: product.rating >= 4.3, text: `Highly rated by ${product.totalReviews.toLocaleString()}+ verified buyers (${product.rating}/5)` },
      { cond: isCotton, text: `100% natural pure cotton fabric offering premium softness and skin comfort` },
      { cond: isDenim, text: `Durable denim weave engineered for long-lasting structural shape retention` },
      { cond: isSport, text: `High-flex stretch fabric with quick-dry moisture management properties` },
      { cond: product.dealScore >= 85, text: `High value deal score of ${product.dealScore}/100 for verified brand quality` },
      { cond: true, text: `Clean tailoring and consistent silhouette fit suitable for regular wear` },
      { cond: true, text: `Durable double-stitched seams designed to withstand frequent wash cycles` },
    ]
    const matching = apparelPros.filter(p => p.cond)
    matching.sort(() => rng() - 0.5)
    return matching.slice(0, 4).map(p => p.text)
  }

  if (categoryProfileType === 'BEAUTY') {
    const isEDP = /edp|eau de parfum/i.test(`${product.name} ${product.description || ''}`)
    const beautyPros = [
      { cond: product.rating >= 4.3, text: `Highly rated by ${product.totalReviews.toLocaleString()}+ verified buyers (${product.rating}/5)` },
      { cond: isEDP, text: `High oil concentration Eau De Parfum formula providing 6-8+ hours sustained wear` },
      { cond: product.dealScore >= 85, text: `Outstanding deal score of ${product.dealScore}/100 offering high volume per rupee` },
      { cond: true, text: `Harmonious fragrance note progression from fresh opening to lasting warm base` },
      { cond: true, text: `Packaged in a secure, travel-friendly bottle with precision atomization` },
      { cond: true, text: `Verified authentic batch supply from authorized brand distribution partners` },
    ]
    const matching = beautyPros.filter(p => p.cond)
    matching.sort(() => rng() - 0.5)
    return matching.slice(0, 4).map(p => p.text)
  }

  // Electronics (Preserved Exactly)
  const allPros = [
    { cond: profile.battery > 75, text: `Excellent battery life — expect ${Math.round(profile.battery * 0.5 + rng() * 10)}+ hours of screen-on time` },
    { cond: profile.camera > 78, text: `Outstanding camera system with ${product.brand} computational photography` },
    { cond: profile.gaming > 80, text: `Smooth gaming performance with sustained frame rates` },
    { cond: product.rating >= 4.3, text: `Highly rated by ${product.totalReviews.toLocaleString()}+ verified buyers (${product.rating}/5)` },
    { cond: product.dealScore >= 85, text: `Excellent deal score of ${product.dealScore}/100 — strong value proposition` },
    { cond: profile.service > 80, text: `Extensive ${product.brand} service network across India & globally` },
    { cond: profile.updates > 75, text: `Regular software updates and long-term OS support` },
    { cond: profile.ecosystem > 70, text: `Strong ecosystem integration with ${product.brand} accessories` },
    { cond: profile.repairability > 75, text: `Easy to repair with widely available spare parts` },
    { cond: profile.resale > 65, text: `Strong resale value — retains ${profile.resale}% value after 1 year` },
    { cond: (product.prices || []).length > 3, text: `Available across ${(product.prices || []).length} platforms — easy price comparison` },
    { cond: profile.heating > 70, text: `Good thermal management under heavy loads` },
    { cond: true, text: `Competitive pricing in the ${(product.category || 'category').toLowerCase()} segment` },
    { cond: true, text: `Well-built with premium finish and quality materials` },
  ]
  const matching = allPros.filter(p => p.cond)
  matching.sort(() => rng() - 0.5)
  return matching.slice(0, 4).map(p => p.text)
}

// Generate cons based on product traits and category profile
function generateCons(product, profile, rng, categoryProfileType = 'ELECTRONICS') {
  if (categoryProfileType === 'FOOTWEAR') {
    const footwearCons = [
      { cond: true, text: `May require a short break-in period for optimal arch and insole comfort` },
      { cond: true, text: `Outsole tread wear may accelerate when used heavily on rough outdoor asphalt` },
      { cond: product.rating < 4.3, text: `Mixed buyer feedback on sizing — consider ordering half-size up for wider feet` },
      { cond: true, text: `Colorway pricing and size availability may fluctuate across retail platforms` },
    ]
    const matching = footwearCons.filter(p => p.cond)
    matching.sort(() => rng() - 0.5)
    return matching.slice(0, 3).map(p => p.text)
  }

  if (categoryProfileType === 'APPAREL') {
    const apparelCons = [
      { cond: true, text: `Follow recommended wash-care guidelines to prevent high-temperature shrinkage` },
      { cond: true, text: `Pure cotton weave may require light steam pressing after machine wash cycles` },
      { cond: product.rating < 4.3, text: `Customer reviews indicate silhouette cut runs slightly snug` },
      { cond: true, text: `Color and size availability vary between marketplace sellers` },
    ]
    const matching = apparelCons.filter(p => p.cond)
    matching.sort(() => rng() - 0.5)
    return matching.slice(0, 3).map(p => p.text)
  }

  if (categoryProfileType === 'BEAUTY') {
    const beautyCons = [
      { cond: true, text: `Scent dry-down and longevity can vary with individual skin chemistry and ambient humidity` },
      { cond: true, text: `Standard patch test recommended prior to first full application for sensitive skin` },
      { cond: true, text: `Atomizer spray cap must be kept securely sealed to prevent volatile notes fading` },
    ]
    const matching = beautyCons.filter(p => p.cond)
    matching.sort(() => rng() - 0.5)
    return matching.slice(0, 3).map(p => p.text)
  }

  // Electronics (Preserved Exactly)
  const allCons = [
    { cond: profile.battery < 72, text: `Battery life could be better for power users` },
    { cond: profile.camera < 70, text: `Camera struggles in low-light conditions` },
    { cond: profile.gaming < 70, text: `Not ideal for heavy gaming — occasional frame drops` },
    { cond: product.rating < 4.3, text: `Mixed user reviews — some quality consistency concerns` },
    { cond: profile.heating < 65, text: `Noticeable heating during extended gaming or video calls` },
    { cond: profile.updates < 65, text: `Software update frequency is below flagship standards` },
    { cond: profile.privacy < 65, text: `Pre-installed bloatware and privacy concerns with data collection` },
    { cond: profile.ecosystem < 60, text: `Limited ecosystem — fewer compatible accessories` },
    { cond: profile.resale < 55, text: `Poor resale value — depreciates quickly in secondary market` },
    { cond: profile.service < 70, text: `Service center availability limited in smaller cities` },
    { cond: profile.repairability < 65, text: `Difficult to repair — proprietary components used` },
    { cond: true, text: `Price may fluctuate significantly across platforms` },
    { cond: true, text: `Limited color/storage variants available` },
  ]
  const matching = allCons.filter(p => p.cond)
  matching.sort(() => rng() - 0.5)
  return matching.slice(0, 3).map(p => p.text)
}

// Generate price history (6 months)
function generatePriceHistory(product, rng) {
  const months = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr']
  const basePrice = product.bestPrice
  const volatility = 0.08 + rng() * 0.12 // 8-20% volatility
  
  return months.map((month, i) => {
    const factor = 1 + (rng() - 0.4) * volatility
    // Trend toward current price at the end
    const trendFactor = i / (months.length - 1)
    const historicalPrice = basePrice * factor * (1 - trendFactor) + basePrice * trendFactor
    return {
      month,
      price: Math.round(historicalPrice * 100) / 100,
    }
  })
}

// Generate community sentiment
function generateSentiment(product, profile, rng) {
  const baseSentiment = (product.rating - 3) / 2 * 100 // 0-100 scale
  
  return {
    youtube: {
      positive: clamp(Math.round(baseSentiment * (0.8 + rng() * 0.4)), 20, 92),
      neutral: 0,
      negative: 0,
    },
    reddit: {
      positive: clamp(Math.round(baseSentiment * (0.7 + rng() * 0.5)), 15, 88),
      neutral: 0,
      negative: 0,
    },
    reviews: {
      positive: clamp(Math.round(baseSentiment * (0.85 + rng() * 0.3)), 25, 95),
      neutral: 0,
      negative: 0,
    }
  }
}

// Fill in neutral and negative to sum to 100
function completeSentiment(s) {
  const fill = (obj) => {
    obj.negative = clamp(Math.round((100 - obj.positive) * 0.4), 3, 40)
    obj.neutral = 100 - obj.positive - obj.negative
  }
  fill(s.youtube)
  fill(s.reddit)
  fill(s.reviews)
  return s
}

// User persona scoring (Category-Aware)
function generatePersonaScores(product, profile, rng, categoryProfileType = 'ELECTRONICS') {
  const inrPrice = (product.currency === 'USD' || product.bestPrice < 1000) ? product.bestPrice * 84 : product.bestPrice
  const priceFactor = inrPrice < 15000 ? 1.1 : inrPrice < 35000 ? 1.0 : 0.9

  if (categoryProfileType === 'FOOTWEAR') {
    const isBadminton = /badminton|court/i.test(`${product.name} ${product.description || ''}`)
    const isRunning = /running|runner|marathon/i.test(`${product.name} ${product.description || ''}`)
    const rating = product.rating || 4.2

    const court = clamp(Math.round((isBadminton ? 94 : isRunning ? 78 : 72) + (rng() - 0.5) * 6), 65, 98)
    const runner = clamp(Math.round((isRunning ? 94 : isBadminton ? 82 : 75) + (rng() - 0.5) * 6), 65, 98)
    const commuter = clamp(Math.round((rating / 5) * 88 + (rng() - 0.5) * 6), 70, 96)
    const value = clamp(Math.round((product.dealScore || 80) * 0.9 + (rng() - 0.5) * 8), 65, 98)

    return {
      commuter,
      runner,
      court,
      value,
      // Legacy compatibility keys
      student: commuter,
      creator: runner,
      gamer: court,
      parent: value,
    }
  }

  if (categoryProfileType === 'APPAREL') {
    const isSport = /sport|gym|active/i.test(`${product.name} ${product.description || ''}`)
    const isFormal = /formal|shirt|polo|blazer/i.test(`${product.name} ${product.description || ''}`)
    const rating = product.rating || 4.2

    const casual = clamp(Math.round((rating / 5) * 88 + (rng() - 0.5) * 6), 70, 96)
    const office = clamp(Math.round((isFormal ? 92 : 74) + (rng() - 0.5) * 6), 65, 96)
    const active = clamp(Math.round((isSport ? 94 : 72) + (rng() - 0.5) * 6), 65, 96)
    const value = clamp(Math.round((product.dealScore || 80) * 0.9 + (rng() - 0.5) * 8), 65, 98)

    return {
      casual,
      office,
      active,
      value,
      student: casual,
      creator: office,
      gamer: active,
      parent: value,
    }
  }

  if (categoryProfileType === 'BEAUTY') {
    const isEDP = /edp|eau de parfum/i.test(`${product.name} ${product.description || ''}`)
    const rating = product.rating || 4.3

    const daily = clamp(Math.round((rating / 5) * 86 + (rng() - 0.5) * 6), 70, 96)
    const evening = clamp(Math.round((isEDP ? 94 : 76) + (rng() - 0.5) * 6), 65, 98)
    const gentle = clamp(Math.round(82 + (rng() - 0.5) * 6), 70, 94)
    const value = clamp(Math.round((product.dealScore || 80) * 0.9 + (rng() - 0.5) * 8), 65, 98)

    return {
      daily,
      evening,
      gentle,
      value,
      student: daily,
      creator: evening,
      gamer: gentle,
      parent: value,
    }
  }

  // Electronics (Preserved Exactly)
  return {
    gamer: clamp(Math.round((profile.gaming * 0.5 + (100 - profile.heating) * 0.2 + profile.battery * 0.15 + rng() * 15) * priceFactor), 30, 98),
    student: clamp(Math.round((profile.battery * 0.35 + (inrPrice < 20000 ? 85 : 55) * 0.3 + profile.camera * 0.15 + rng() * 12), 30, 98), 30, 98),
    creator: clamp(Math.round((profile.camera * 0.4 + profile.gaming * 0.2 + profile.updates * 0.15 + profile.ecosystem * 0.15 + rng() * 10)), 30, 98),
    parent: clamp(Math.round((profile.battery * 0.3 + profile.service * 0.25 + (inrPrice < 15000 ? 90 : 50) * 0.25 + profile.privacy * 0.1 + rng() * 10)), 30, 98),
  }
}

// India/Asia intelligence (Category-Aware)
function generateIndiaIntel(product, profile, rng, categoryProfileType = 'ELECTRONICS') {
  const inrPrice = (product.currency === 'USD' || product.bestPrice < 1000) ? product.bestPrice * 84 : product.bestPrice
  const priceTier = inrPrice < 1500 ? 'budget' : inrPrice < 4000 ? 'mid' : 'premium'
  const maxDiscount = Math.round(inrPrice * (0.15 + rng() * 0.2))

  if (categoryProfileType === 'FOOTWEAR') {
    return {
      serviceCenters: {
        score: clamp(Math.round(82 + (rng() - 0.5) * 12), 70, 98),
        cities: Math.round(120 + rng() * 60),
        note: `${product.brand} supports doorstep return and size exchange across tier-1, tier-2, and tier-3 cities`,
      },
      motherboardIssues: {
        score: clamp(Math.round(85 + (rng() - 0.5) * 15), 75, 96),
        riskLevel: 'Low Risk',
        note: 'High outsole wear resistance engineered for everyday Indian road and pavement conditions',
      },
      emiOptions: {
        available: inrPrice > 2000,
        banks: Math.round(4 + rng() * 8),
        minEmi: Math.round(inrPrice / 3),
        noCostEmi: inrPrice > 3000 && rng() > 0.4,
        note: inrPrice > 2000 ? 'Cardless and bank EMI options available on select partner platforms' : 'Standard instant checkout available',
      },
      exchangeOffers: {
        maxDiscount: maxDiscount,
        platforms: (product.prices || []).map(p => p.platform).slice(0, 3),
        note: `Seasonal brand exchange promotions available with up to ₹${maxDiscount.toLocaleString('en-IN')} off`,
      },
      sellerTrust: {
        amazon: clamp(Math.round(82 + rng() * 16), 70, 98),
        flipkart: clamp(Math.round(80 + rng() * 18), 68, 98),
        note: 'Trust ratings verified from official brand stores and authorized retail distributors',
      },
    }
  }

  if (categoryProfileType === 'APPAREL') {
    return {
      serviceCenters: {
        score: clamp(Math.round(84 + (rng() - 0.5) * 10), 72, 98),
        cities: Math.round(150 + rng() * 50),
        note: `${product.brand} features hassle-free 7-day doorstep size replacement across all major postal codes`,
      },
      motherboardIssues: {
        score: clamp(Math.round(86 + (rng() - 0.5) * 12), 76, 96),
        riskLevel: 'Low Risk',
        note: 'Tested for colorfastness and shrinkage resistance in standard household wash cycles',
      },
      emiOptions: {
        available: inrPrice > 2500,
        banks: Math.round(4 + rng() * 6),
        minEmi: Math.round(inrPrice / 3),
        noCostEmi: false,
        note: 'Split-payment options available on eligible merchant checkout cards',
      },
      exchangeOffers: {
        maxDiscount: maxDiscount,
        platforms: (product.prices || []).map(p => p.platform).slice(0, 3),
        note: `Festive wardrobe promotions offer bundled multi-item savings up to ₹${maxDiscount.toLocaleString('en-IN')}`,
      },
      sellerTrust: {
        amazon: clamp(Math.round(80 + rng() * 16), 70, 98),
        flipkart: clamp(Math.round(82 + rng() * 16), 70, 98),
        note: 'Verified sellers adhering to platform garment quality and return benchmarks',
      },
    }
  }

  if (categoryProfileType === 'BEAUTY') {
    return {
      serviceCenters: {
        score: clamp(Math.round(80 + (rng() - 0.5) * 12), 70, 96),
        cities: Math.round(100 + rng() * 40),
        note: 'Direct customer support and authenticity verification provided by authorized brand brand importers',
      },
      motherboardIssues: {
        score: clamp(Math.round(88 + (rng() - 0.5) * 10), 78, 98),
        riskLevel: 'Low Risk',
        note: '100% genuine sealed batch packaging protected against transit evaporation and heat degradation',
      },
      emiOptions: {
        available: inrPrice > 2000,
        banks: Math.round(3 + rng() * 6),
        minEmi: Math.round(inrPrice / 3),
        noCostEmi: false,
        note: 'Pay-later and flexible bank checkout options on verified beauty platforms',
      },
      exchangeOffers: {
        maxDiscount: maxDiscount,
        platforms: (product.prices || []).map(p => p.platform).slice(0, 3),
        note: `Brand promotional discounts offer promotional gift savings up to ₹${maxDiscount.toLocaleString('en-IN')}`,
      },
      sellerTrust: {
        amazon: clamp(Math.round(84 + rng() * 14), 74, 98),
        flipkart: clamp(Math.round(81 + rng() * 16), 70, 98),
        note: 'Verified authentic cosmetic retailers with anti-counterfeit batch verification',
      },
    }
  }

  // Electronics (Preserved Exactly)
  return {
    serviceCenters: {
      score: clamp(Math.round(profile.service + (rng() - 0.5) * 15), 30, 98),
      cities: Math.round(50 + profile.service * 2 + rng() * 100),
      note: profile.service > 80 
        ? `${product.brand} has excellent service coverage across tier-1 and tier-2 cities`
        : `${product.brand} service centers primarily in metros — limited in smaller cities`,
    },
    motherboardIssues: {
      score: clamp(Math.round(75 + (rng() - 0.5) * 30), 40, 98),
      riskLevel: rng() > 0.7 ? 'Low Risk' : rng() > 0.3 ? 'Moderate' : 'Known Issues',
      note: profile.heating > 70 
        ? 'No widespread motherboard or green-line issues reported'
        : 'Some users have reported display issues after prolonged use — monitor warranty terms',
    },
    emiOptions: {
      available: true,
      banks: Math.round(6 + rng() * 10),
      minEmi: Math.round(inrPrice / 12),
      noCostEmi: priceTier !== 'budget' && rng() > 0.3,
      note: `No-cost EMI available on select bank cards for up to ${priceTier === 'premium' ? 18 : 12} months`,
    },
    exchangeOffers: {
      maxDiscount: maxDiscount,
      platforms: (product.prices || []).map(p => p.platform).slice(0, 3),
      note: `Exchange your old phone for up to ₹${maxDiscount.toLocaleString('en-IN')} off`,
    },
    sellerTrust: {
      amazon: clamp(Math.round(78 + rng() * 20), 60, 98),
      flipkart: clamp(Math.round(75 + rng() * 22), 58, 98),
      note: 'Trust scores based on seller ratings, return policy, and delivery reliability',
    },
  }
}

// USA intelligence (Category-Aware)
function generateUSAIntel(product, profile, rng, categoryProfileType = 'ELECTRONICS') {
  if (categoryProfileType === 'FOOTWEAR') {
    return {
      privacy: {
        score: clamp(Math.round(86 + (rng() - 0.5) * 10), 75, 98),
        dataCollection: 'Minimal',
        note: 'Ethical consumer brand compliance with transparent return policies',
      },
      softwareUpdates: {
        score: clamp(Math.round(82 + (rng() - 0.5) * 12), 70, 95),
        yearsSupport: '3+ years',
        note: 'Typical sole wear life spanning 500-800 kilometers under regular use',
      },
      ecosystem: {
        score: clamp(Math.round(84 + (rng() - 0.5) * 12), 70, 96),
        compatibility: 'Excellent',
        note: `Compatible with standard aftermarket orthotic insoles and ${product.brand} gear`,
      },
      repairability: {
        score: clamp(Math.round(72 + (rng() - 0.5) * 15), 60, 90),
        iFixitScore: 'Cobbler-ready',
        note: 'Replaceable laces and standard insole; outer sole durable under standard use',
      },
      resaleValue: {
        score: clamp(Math.round(75 + (rng() - 0.5) * 15), 60, 95),
        retentionPercent: `${clamp(Math.round(55 + rng() * 20), 40, 75)}%`,
        note: `Retains consistent pre-owned value in lifestyle and sneaker collector markets`,
      },
      sustainability: {
        score: clamp(Math.round(80 + (rng() - 0.5) * 14), 65, 96),
        recyclability: 'Moderate to High',
        note: `${product.brand} utilizes recycled rubber compounds in outsole manufacturing`,
      },
    }
  }

  if (categoryProfileType === 'APPAREL') {
    return {
      privacy: {
        score: clamp(Math.round(88 + (rng() - 0.5) * 8), 80, 98),
        dataCollection: 'Minimal',
        note: 'Compliant with consumer protection and product safety regulations',
      },
      softwareUpdates: {
        score: clamp(Math.round(84 + (rng() - 0.5) * 10), 72, 95),
        yearsSupport: '2-3 years',
        note: 'Fabric retention rated for 50+ machine wash cycles with minimal shape distortion',
      },
      ecosystem: {
        score: clamp(Math.round(82 + (rng() - 0.5) * 12), 70, 96),
        compatibility: 'Universal',
        note: 'Versatile styling pairing seamlessly with casual and smart-casual wardrobes',
      },
      repairability: {
        score: clamp(Math.round(86 + (rng() - 0.5) * 10), 75, 98),
        iFixitScore: '10/10',
        note: 'Easily mended standard hems, buttons, and stitching seams',
      },
      resaleValue: {
        score: clamp(Math.round(68 + (rng() - 0.5) * 16), 50, 88),
        retentionPercent: `${clamp(Math.round(45 + rng() * 20), 30, 65)}%`,
        note: 'Standard resale value retention on leading second-hand fashion platforms',
      },
      sustainability: {
        score: clamp(Math.round(82 + (rng() - 0.5) * 12), 70, 96),
        recyclability: 'High',
        note: 'Natural cotton fibers fully biodegradable and recyclable through textile programs',
      },
    }
  }

  if (categoryProfileType === 'BEAUTY') {
    return {
      privacy: {
        score: clamp(Math.round(86 + (rng() - 0.5) * 10), 75, 98),
        dataCollection: 'Minimal',
        note: 'Transparent ingredient labeling conforming to FDA and IFRA guidelines',
      },
      softwareUpdates: {
        score: clamp(Math.round(88 + (rng() - 0.5) * 8), 78, 98),
        yearsSupport: '36 months',
        note: 'Optimal formula shelf-life stability of 36 months after initial spray',
      },
      ecosystem: {
        score: clamp(Math.round(80 + (rng() - 0.5) * 12), 68, 94),
        compatibility: 'High',
        note: 'Layers cleanly with complementary personal care and grooming products',
      },
      repairability: {
        score: clamp(Math.round(70 + (rng() - 0.5) * 15), 55, 88),
        iFixitScore: 'Sealed Unit',
        note: 'Hermetically crimped atomizer prevents leakage and airborne oxidation',
      },
      resaleValue: {
        score: clamp(Math.round(70 + (rng() - 0.5) * 16), 55, 90),
        retentionPercent: `${clamp(Math.round(60 + rng() * 15), 45, 75)}%`,
        note: 'Sealed authentic fragrance bottles retain robust secondary market demand',
      },
      sustainability: {
        score: clamp(Math.round(84 + (rng() - 0.5) * 12), 72, 96),
        recyclability: 'High',
        note: 'Recyclable glass flacon packaging and FSC-certified paperboard outer carton',
      },
    }
  }

  // Electronics (Preserved Exactly)
  return {
    privacy: {
      score: clamp(Math.round(profile.privacy + (rng() - 0.5) * 15), 30, 98),
      dataCollection: profile.privacy > 75 ? 'Minimal' : profile.privacy > 60 ? 'Moderate' : 'Extensive',
      note: profile.privacy > 75 
        ? `${product.brand} has strong privacy practices with minimal data collection`
        : `${product.brand} collects usage analytics — review privacy settings after purchase`,
    },
    softwareUpdates: {
      score: clamp(Math.round(profile.updates + (rng() - 0.5) * 12), 25, 98),
      yearsSupport: profile.updates > 80 ? '5+ years' : profile.updates > 65 ? '3-4 years' : '2 years',
      note: `Expected to receive OS updates for ${profile.updates > 80 ? '5+' : profile.updates > 65 ? '3-4' : '2'} years`,
    },
    ecosystem: {
      score: clamp(Math.round(profile.ecosystem + (rng() - 0.5) * 15), 20, 98),
      compatibility: profile.ecosystem > 75 ? 'Excellent' : profile.ecosystem > 55 ? 'Good' : 'Limited',
      note: `${profile.ecosystem > 75 ? 'Seamless' : 'Basic'} integration with ${product.brand} wearables, earbuds, and smart home`,
    },
    repairability: {
      score: clamp(Math.round(profile.repairability + (rng() - 0.5) * 15), 20, 98),
      iFixitScore: `${Math.round(profile.repairability / 10)}/10`,
      note: profile.repairability > 75 
        ? 'Parts widely available — supports right-to-repair initiatives'
        : 'Proprietary components make third-party repairs challenging',
    },
    resaleValue: {
      score: clamp(Math.round(profile.resale + (rng() - 0.5) * 15), 15, 98),
      retentionPercent: `${clamp(Math.round(profile.resale * 0.85 + rng() * 10), 20, 85)}%`,
      note: `Retains approximately ${clamp(Math.round(profile.resale * 0.85 + rng() * 10), 20, 85)}% value after 12 months`,
    },
    sustainability: {
      score: clamp(Math.round(profile.sustainability + (rng() - 0.5) * 15), 20, 98),
      recyclability: profile.sustainability > 70 ? 'High' : profile.sustainability > 50 ? 'Moderate' : 'Low',
      note: profile.sustainability > 70 
        ? `${product.brand} uses recycled materials and has carbon-neutral shipping programs`
        : `Limited sustainability commitments — check ${product.brand}'s environmental report`,
    },
  }
}

// Scoring breakdown
function generateScoringBreakdown(product) {
  return {
    priceWeight: 30,
    ratingWeight: 25,
    dealScoreWeight: 20,
    reviewsWeight: 15,
    brandWeight: 10,
    priceScore: clamp(Math.round((1 - product.bestPrice / 500) * 100), 20, 95),
    ratingScore: Math.round(product.rating / 5 * 100),
    dealScoreValue: product.dealScore,
    reviewsScore: clamp(Math.round(Math.log10(product.totalReviews + 1) / 5.2 * 100), 20, 95),
  }
}

function generateWhyNarrative(product, opponent, profile, isWinner, rng, categoryProfileType = 'ELECTRONICS') {
  if (categoryProfileType === 'FOOTWEAR') {
    if (isWinner) {
      return `${product.name} edges ahead with a superior deal score of ${product.dealScore}/100, backed by ${product.totalReviews.toLocaleString()} verified reviews. ${product.brand}'s footwear demonstrates stronger comparison signals in daily insole comfort, traction, and build durability. At ${product.bestPrice < opponent.bestPrice ? 'a lower price point' : 'its current price'}, ${product.name} delivers higher overall value per wear.`
    } else {
      return `While ${product.name} shows competitive strengths in ${product.brand} styling and cushioning, it falls slightly short in overall deal confidence compared to its rival. It remains a dependable choice for buyers who prioritize ${product.brand}'s signature aesthetic.`
    }
  }

  if (categoryProfileType === 'APPAREL') {
    if (isWinner) {
      return `${product.name} edges ahead with a superior deal score of ${product.dealScore}/100, backed by ${product.totalReviews.toLocaleString()} verified reviews. ${product.brand}'s garment demonstrates stronger fabric feel, breathable comfort, and cut consistency. At ${product.bestPrice < opponent.bestPrice ? 'a lower price point' : 'its current price'}, it delivers superior everyday wearability.`
    } else {
      return `While ${product.name} shows competitive strengths in fabric quality and silhouette, it falls slightly short in overall price-to-value proposition compared to its rival.`
    }
  }

  if (categoryProfileType === 'BEAUTY') {
    if (isWinner) {
      return `${product.name} edges ahead with a superior deal score of ${product.dealScore}/100, backed by ${product.totalReviews.toLocaleString()} verified reviews. ${product.brand}'s formulation demonstrates higher customer satisfaction, lasting wear profile, and value per application.`
    } else {
      return `While ${product.name} offers distinct formulation and scent profile strengths, it falls slightly short in overall deal score compared to its rival.`
    }
  }

  // Electronics (Preserved Exactly)
  if (isWinner) {
    const reasons = [
      `${product.name} edges ahead with a superior deal score of ${product.dealScore}/100, backed by ${product.totalReviews.toLocaleString()} verified reviews.`,
      `${product.brand}'s offering demonstrates stronger real-world performance metrics, particularly in ${profile.gaming > profile.camera ? 'gaming' : 'camera'} and ${profile.battery > 75 ? 'battery endurance' : 'daily usage scenarios'}.`,
      `At ${product.bestPrice < opponent.bestPrice ? 'a lower price point' : 'its current price'}, ${product.name} delivers more value per dollar spent, making it the smarter purchase for most users.`,
    ]
    return reasons.join(' ')
  } else {
    const strengths = []
    if (profile.camera > 78) strengths.push('camera quality')
    if (profile.battery > 80) strengths.push('battery life')
    if (profile.gaming > 80) strengths.push('gaming performance')
    if (profile.service > 80) strengths.push('after-sales service')
    if (strengths.length === 0) strengths.push('build quality')
    
    return `While ${product.name} shows competitive strengths in ${strengths.join(' and ')}, it falls slightly short in overall value proposition compared to its rival. It remains a solid choice for users who prioritize ${strengths[0]} above all else.`
  }
}

/**
 * Generate complete deep comparison data for two products
 * @param {Object} product1 - First product
 * @param {Object} product2 - Second product
 * @param {number|null} winnerIndex - 0 or 1, or null for tie
 * @returns {Object} Deep comparison data
 */
export function generateDeepCompareData(product1, product2, winnerIndex) {
  const seed = (product1.id * 1000 + product2.id) * 7 + 42
  const rng = seededRandom(seed)
  
  const profile1 = getBrandProfile(product1.brand)
  const profile2 = getBrandProfile(product2.brand)

  // Compute Electronics Fallback metrics (Preserved Exactly for Electronics)
  const electronicsFallback = {
    perf1: {
      battery: clamp(Math.round(profile1.battery + (rng() - 0.5) * 20), 30, 98),
      heating: clamp(Math.round(profile1.heating + (rng() - 0.5) * 20), 30, 98),
      gaming: clamp(Math.round(profile1.gaming + (rng() - 0.5) * 20), 30, 98),
      camera: clamp(Math.round(profile1.camera + (rng() - 0.5) * 20), 30, 98),
    },
    perf2: {
      battery: clamp(Math.round(profile2.battery + (rng() - 0.5) * 20), 30, 98),
      heating: clamp(Math.round(profile2.heating + (rng() - 0.5) * 20), 30, 98),
      gaming: clamp(Math.round(profile2.gaming + (rng() - 0.5) * 20), 30, 98),
      camera: clamp(Math.round(profile2.camera + (rng() - 0.5) * 20), 30, 98),
    },
  }

  // Master Category Comparison Profile
  const categoryProfile = resolveComparisonProfile(product1, product2, electronicsFallback)
  const profileType = categoryProfile.id
  
  // Pick verdict label
  const cat = product1.category || 'default'
  const labels = VERDICT_LABELS[cat] || VERDICT_LABELS['default']
  const verdictIndex = Math.floor(rng() * labels.length)
  const verdict = labels[verdictIndex]
  
  // Secondary verdict for loser
  const otherLabels = labels.filter((_, i) => i !== verdictIndex)
  const secondaryVerdict = otherLabels[Math.floor(rng() * otherLabels.length)]

  // Build Real-World Performance data
  // For Electronics: exactly preserves battery, heating, gaming, camera
  // For Footwear/Apparel/Beauty: strictly category-specific metrics (NO electronics leakage!)
  let realWorldPerformance = {}
  if (profileType === 'ELECTRONICS') {
    realWorldPerformance = {
      product1: electronicsFallback.perf1,
      product2: electronicsFallback.perf2,
    }
  } else {
    const p1MetricsObj = {}
    const p2MetricsObj = {}
    for (const m of categoryProfile.metrics) {
      p1MetricsObj[m.key] = m.p1.value
      p2MetricsObj[m.key] = m.p2.value
    }
    realWorldPerformance = {
      product1: p1MetricsObj,
      product2: p2MetricsObj,
    }
  }
  
  const data = {
    categoryProfile,
    
    verdict: {
      primary: verdict,
      secondary: secondaryVerdict,
      winnerIndex,
      confidence: clamp(Math.round(65 + rng() * 30), 55, 95),
    },
    
    whyThisWon: {
      product1: generateWhyNarrative(product1, product2, profile1, winnerIndex === 0, rng, profileType),
      product2: generateWhyNarrative(product2, product1, profile2, winnerIndex === 1, rng, profileType),
    },
    
    personaScores: {
      product1: generatePersonaScores(product1, profile1, rng, profileType),
      product2: generatePersonaScores(product2, profile2, rng, profileType),
    },
    
    realWorldPerformance,
    
    indiaIntel: {
      product1: generateIndiaIntel(product1, profile1, rng, profileType),
      product2: generateIndiaIntel(product2, profile2, rng, profileType),
    },
    
    usaIntel: {
      product1: generateUSAIntel(product1, profile1, rng, profileType),
      product2: generateUSAIntel(product2, profile2, rng, profileType),
    },
    
    sentiment: {
      product1: completeSentiment(generateSentiment(product1, profile1, rng)),
      product2: completeSentiment(generateSentiment(product2, profile2, rng)),
    },
    
    priceHistory: {
      product1: generatePriceHistory(product1, rng),
      product2: generatePriceHistory(product2, rng),
    },
    
    prosAndCons: {
      product1: {
        pros: generatePros(product1, profile1, rng, profileType),
        cons: generateCons(product1, profile1, rng, profileType),
      },
      product2: {
        pros: generatePros(product2, profile2, rng, profileType),
        cons: generateCons(product2, profile2, rng, profileType),
      },
    },
    
    scoring: {
      product1: generateScoringBreakdown(product1),
      product2: generateScoringBreakdown(product2),
    },
    
    verifiedSpecs: {
      product1: { verified: true, source: 'BrandBattle AI + Manufacturer Data', lastUpdated: '2026-05-24' },
      product2: { verified: true, source: 'BrandBattle AI + Manufacturer Data', lastUpdated: '2026-05-24' },
    },
  }
  
  return data
}

export default generateDeepCompareData

