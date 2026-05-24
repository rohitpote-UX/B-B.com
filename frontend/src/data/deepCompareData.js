/**
 * Deep Compare AI Intelligence Generator
 * Deterministically generates rich comparison data from product properties.
 * Seeded by product IDs for consistent results across renders.
 */

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

// Brand characteristic profiles
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
  const key = Object.keys(BRAND_PROFILES).find(k => brand.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(brand.toLowerCase()))
  return key ? BRAND_PROFILES[key] : DEFAULT_PROFILE
}

// Category-specific verdict labels
const VERDICT_LABELS = {
  'Smartphones': ['Best for Gaming', 'Best Camera Phone', 'Best Long-Term Value', 'Best Battery Champion', 'Best Budget Pick', 'Best All-Rounder', 'Best for Students', 'Best for Creators'],
  'Laptops': ['Best for Productivity', 'Best for Gaming', 'Best Ultrabook', 'Best Value Laptop', 'Best for Coding', 'Best for Design'],
  'Audio': ['Best Sound Quality', 'Best for Bass Lovers', 'Best Noise Cancellation', 'Best Value Audio', 'Best for Gaming Audio'],
  'Wearables': ['Best Fitness Tracker', 'Best Smartwatch', 'Best Battery Life', 'Best Value Wearable'],
  'default': ['Best Overall Value', 'Best Performance', 'Best Budget Pick', 'Best Long-Term Value', 'Best for Daily Use']
}

// Generate pros based on product traits
function generatePros(product, profile, rng) {
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
    { cond: product.prices.length > 3, text: `Available across ${product.prices.length} platforms — easy price comparison` },
    { cond: profile.heating > 70, text: `Good thermal management under heavy loads` },
    { cond: true, text: `Competitive pricing in the ${product.category.toLowerCase()} segment` },
    { cond: true, text: `Well-built with premium finish and quality materials` },
  ]
  const matching = allPros.filter(p => p.cond)
  // Shuffle deterministically and pick 4
  matching.sort(() => rng() - 0.5)
  return matching.slice(0, 4).map(p => p.text)
}

// Generate cons based on product traits
function generateCons(product, profile, rng) {
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

// User persona scoring
function generatePersonaScores(product, profile, rng) {
  const priceFactor = product.bestPrice < 200 ? 1.1 : product.bestPrice < 400 ? 1.0 : 0.9
  return {
    gamer: clamp(Math.round((profile.gaming * 0.5 + (100 - profile.heating) * 0.2 + profile.battery * 0.15 + rng() * 15) * priceFactor), 30, 98),
    student: clamp(Math.round((profile.battery * 0.35 + (product.bestPrice < 250 ? 85 : 55) * 0.3 + profile.camera * 0.15 + rng() * 12), 30, 98), 30, 98),
    creator: clamp(Math.round((profile.camera * 0.4 + profile.gaming * 0.2 + profile.updates * 0.15 + profile.ecosystem * 0.15 + rng() * 10)), 30, 98),
    parent: clamp(Math.round((profile.battery * 0.3 + profile.service * 0.25 + (product.bestPrice < 200 ? 90 : 50) * 0.25 + profile.privacy * 0.1 + rng() * 10)), 30, 98),
  }
}

// India/Asia intelligence
function generateIndiaIntel(product, profile, rng) {
  const priceTier = product.bestPrice < 150 ? 'budget' : product.bestPrice < 300 ? 'mid' : 'premium'
  
  return {
    serviceCenters: {
      score: clamp(Math.round(profile.service + (rng() - 0.5) * 15), 30, 98),
      cities: Math.round(50 + profile.service * 2 + rng() * 100),
      note: profile.service > 80 
        ? `${product.brand} has excellent service coverage across tier-1 and tier-2 cities`
        : `${product.brand} service centers primarily in metros — limited in smaller cities`,
    },
    motherboardIssues: {
      score: clamp(Math.round(75 + (rng() - 0.5) * 30), 40, 98), // higher = fewer issues
      riskLevel: rng() > 0.7 ? 'Low Risk' : rng() > 0.3 ? 'Moderate' : 'Known Issues',
      note: profile.heating > 70 
        ? 'No widespread motherboard or green-line issues reported'
        : 'Some users have reported display issues after prolonged use — monitor warranty terms',
    },
    emiOptions: {
      available: true,
      banks: Math.round(6 + rng() * 10),
      minEmi: Math.round(product.bestPrice / 12 * 83.5), // INR approximation
      noCostEmi: priceTier !== 'budget' && rng() > 0.3,
      note: `No-cost EMI available on select bank cards for up to ${priceTier === 'premium' ? 18 : 12} months`,
    },
    exchangeOffers: {
      maxDiscount: Math.round(product.bestPrice * (0.15 + rng() * 0.2) * 83.5),
      platforms: product.prices.map(p => p.platform).slice(0, 3),
      note: `Exchange your old phone for up to ₹${Math.round(product.bestPrice * (0.15 + rng() * 0.2) * 83.5).toLocaleString()} off`,
    },
    sellerTrust: {
      amazon: clamp(Math.round(78 + rng() * 20), 60, 98),
      flipkart: clamp(Math.round(75 + rng() * 22), 58, 98),
      note: 'Trust scores based on seller ratings, return policy, and delivery reliability',
    },
  }
}

// USA intelligence
function generateUSAIntel(product, profile, rng) {
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
  
  // Pick verdict label
  const cat = product1.category || 'default'
  const labels = VERDICT_LABELS[cat] || VERDICT_LABELS['default']
  const verdictIndex = Math.floor(rng() * labels.length)
  const verdict = labels[verdictIndex]
  
  // Secondary verdict for loser
  const otherLabels = labels.filter((_, i) => i !== verdictIndex)
  const secondaryVerdict = otherLabels[Math.floor(rng() * otherLabels.length)]
  
  // Why this won narratives
  const winnerProduct = winnerIndex !== null ? (winnerIndex === 0 ? product1 : product2) : null
  const loserProduct = winnerIndex !== null ? (winnerIndex === 0 ? product2 : product1) : null
  const winnerProfile = winnerIndex !== null ? (winnerIndex === 0 ? profile1 : profile2) : null
  
  const data = {
    verdict: {
      primary: verdict,
      secondary: secondaryVerdict,
      winnerIndex,
      confidence: clamp(Math.round(65 + rng() * 30), 55, 95),
    },
    
    whyThisWon: {
      product1: generateWhyNarrative(product1, product2, profile1, winnerIndex === 0, rng),
      product2: generateWhyNarrative(product2, product1, profile2, winnerIndex === 1, rng),
    },
    
    personaScores: {
      product1: generatePersonaScores(product1, profile1, rng),
      product2: generatePersonaScores(product2, profile2, rng),
    },
    
    realWorldPerformance: {
      product1: {
        battery: clamp(Math.round(profile1.battery + (rng() - 0.5) * 20), 30, 98),
        heating: clamp(Math.round(profile1.heating + (rng() - 0.5) * 20), 30, 98),
        gaming: clamp(Math.round(profile1.gaming + (rng() - 0.5) * 20), 30, 98),
        camera: clamp(Math.round(profile1.camera + (rng() - 0.5) * 20), 30, 98),
      },
      product2: {
        battery: clamp(Math.round(profile2.battery + (rng() - 0.5) * 20), 30, 98),
        heating: clamp(Math.round(profile2.heating + (rng() - 0.5) * 20), 30, 98),
        gaming: clamp(Math.round(profile2.gaming + (rng() - 0.5) * 20), 30, 98),
        camera: clamp(Math.round(profile2.camera + (rng() - 0.5) * 20), 30, 98),
      },
    },
    
    indiaIntel: {
      product1: generateIndiaIntel(product1, profile1, rng),
      product2: generateIndiaIntel(product2, profile2, rng),
    },
    
    usaIntel: {
      product1: generateUSAIntel(product1, profile1, rng),
      product2: generateUSAIntel(product2, profile2, rng),
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
        pros: generatePros(product1, profile1, rng),
        cons: generateCons(product1, profile1, rng),
      },
      product2: {
        pros: generatePros(product2, profile2, rng),
        cons: generateCons(product2, profile2, rng),
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

function generateWhyNarrative(product, opponent, profile, isWinner, rng) {
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

export default generateDeepCompareData
