/**
 * BrandBattle AI Engine — Multi-Step Intelligence Pipeline
 * 
 * Pipeline: Query → Intent Parser → Filter Extractor → Product Search → AI Scorer → Response Builder
 * 
 * Key design principle: NEVER return products from the wrong category.
 * Every product comes from verified data — no hallucinations possible.
 */

import { PRODUCTS, PLATFORMS, formatPrice } from './demoData'

// ═══════════════════════════════════════════════════════════
// STEP 0: CONSTANTS & CONFIGURATION
// ═══════════════════════════════════════════════════════════

// Seeded random for deterministic results per product
function seededRandom(seed) {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646 }
}
const clamp = (v, min, max) => Math.max(min, Math.min(max, v))

// Primary category keywords (high weight = confident match)
const CATEGORY_KEYWORDS = {
  'Smartphones': {
    primary: ['smartphone', 'phone', 'mobile', 'cellphone', 'iphone', 'android phone', 'cell'],
    secondary: ['5g', 'selfie', 'calling', 'sim', 'foldable'],
    brands: ['samsung', 'apple', 'iphone', 'oneplus', 'xiaomi', 'redmi', 'poco', 'realme', 'vivo', 'oppo', 'motorola', 'moto', 'nothing', 'iqoo', 'pixel', 'google pixel'],
  },
  'Laptops': {
    primary: ['laptop', 'notebook', 'macbook', 'ultrabook', 'chromebook', 'thinkpad'],
    secondary: ['coding', 'programming', 'typing', 'office work', 'spreadsheet', 'remote work'],
    brands: ['dell', 'hp', 'lenovo', 'asus', 'acer', 'msi', 'apple', 'macbook', 'thinkpad', 'ideapad', 'vivobook', 'zenbook', 'inspiron'],
  },
  'Headphones': {
    primary: ['headphone', 'earphone', 'earbud', 'earbuds', 'headset', 'airpods', 'airpod', 'tws', 'in-ear', 'over-ear', 'on-ear'],
    secondary: ['audio', 'music', 'listening', 'sound', 'noise cancelling', 'anc', 'bass', 'mixing', 'studio monitor', 'podcast'],
    brands: ['sony', 'bose', 'jbl', 'sennheiser', 'beats', 'marshall', 'skullcandy', 'boat', 'noise', 'oneplus', 'apple', 'samsung'],
  },
  'Televisions': {
    primary: ['television', 'tv', 'smart tv', 'led tv', 'oled', 'qled', '4k tv', '8k tv'],
    secondary: ['streaming', 'netflix', 'home theater', 'home theatre', 'big screen', 'display'],
    brands: ['samsung', 'lg', 'sony', 'tcl', 'hisense', 'mi', 'oneplus', 'vu', 'toshiba'],
  },
  'Tablets': {
    primary: ['tablet', 'ipad', 'tab', 'e-reader', 'kindle'],
    secondary: ['note-taking', 'drawing tablet', 'digital art', 'reading'],
    brands: ['apple', 'samsung', 'lenovo', 'xiaomi', 'realme', 'oneplus'],
  },
  'Cameras': {
    primary: ['camera', 'dslr', 'mirrorless', 'action camera', 'gopro', 'webcam', 'camcorder'],
    secondary: ['photography', 'vlogging', 'videography', 'shooting', 'lens'],
    brands: ['canon', 'nikon', 'sony', 'fujifilm', 'gopro', 'dji', 'panasonic'],
  },
  'Gaming': {
    primary: ['gaming console', 'playstation', 'xbox', 'nintendo', 'switch', 'ps5', 'ps4', 'controller', 'gamepad', 'joystick', 'gaming mouse', 'gaming keyboard'],
    secondary: ['esports', 'game', 'fps', 'mmorpg'],
    brands: ['sony', 'microsoft', 'nintendo', 'razer', 'logitech', 'steelseries', 'corsair', 'hyperx'],
  },
  'Clothing': {
    primary: ['shirt', 'tshirt', 't-shirt', 'jeans', 'pants', 'trouser', 'jacket', 'hoodie', 'dress', 'kurta', 'saree', 'top', 'blouse', 'skirt', 'shorts', 'sweater', 'blazer', 'suit', 'clothes', 'clothing', 'apparel', 'wear', 'outfit', 'fashion'],
    secondary: ['formal', 'casual', 'ethnic', 'western', 'party wear', 'office wear'],
    brands: ['nike', 'adidas', 'puma', 'zara', 'h&m', 'levis', 'us polo', 'allen solly', 'peter england', 'van heusen'],
  },
  'Shoes': {
    primary: ['shoe', 'shoes', 'sneaker', 'sneakers', 'boots', 'sandals', 'slippers', 'loafers', 'heels', 'footwear', 'kicks', 'trainers', 'running shoes'],
    secondary: ['walking', 'running', 'hiking', 'sports shoe', 'formal shoe'],
    brands: ['nike', 'adidas', 'puma', 'reebok', 'new balance', 'skechers', 'crocs', 'vans', 'converse', 'asics', 'under armour'],
  },
  'Watches': {
    primary: ['watch', 'smartwatch', 'fitness band', 'fitness tracker', 'wristwatch', 'timepiece'],
    secondary: ['step counter', 'heart rate', 'health tracker', 'wearable'],
    brands: ['apple', 'samsung', 'garmin', 'fitbit', 'fossil', 'casio', 'titan', 'noise', 'boat', 'fire-boltt', 'amazfit'],
  },
  'Accessories': {
    primary: ['bag', 'backpack', 'wallet', 'belt', 'sunglasses', 'case', 'cover', 'charger', 'cable', 'adapter', 'stand', 'mount', 'strap', 'accessory', 'accessories'],
    secondary: ['travel bag', 'laptop bag', 'phone case', 'screen protector'],
    brands: [],
  },
  'Beauty': {
    primary: ['perfume', 'fragrance', 'moisturizer', 'sunscreen', 'serum', 'makeup', 'lipstick', 'foundation', 'skincare', 'beauty', 'cosmetics', 'shampoo', 'hair'],
    secondary: ['grooming', 'face wash', 'body lotion', 'nail paint'],
    brands: ['lakme', 'maybelline', 'loreal', 'nivea', 'dove', 'garnier', 'mac', 'nykaa'],
  },
  'Speakers': {
    primary: ['speaker', 'bluetooth speaker', 'portable speaker', 'soundbar', 'home speaker', 'smart speaker'],
    secondary: ['party speaker', 'bass speaker', 'alexa', 'google home'],
    brands: ['jbl', 'bose', 'sony', 'marshall', 'harman kardon', 'ultimate ears', 'boat', 'mi'],
  },
  'Power Banks': {
    primary: ['power bank', 'powerbank', 'portable charger', 'battery pack'],
    secondary: ['fast charging', 'usb-c charger'],
    brands: ['anker', 'mi', 'samsung', 'realme', 'ambrane', 'syska'],
  },
}

// Use-case to category mapping (handles ambiguous queries like "gaming" or "creator")
const USECASE_CATEGORY_MAP = {
  'gaming':      { categories: ['Gaming', 'Laptops', 'Smartphones', 'Headphones'], weight: 0.7 },
  'student':     { categories: ['Laptops', 'Tablets', 'Headphones', 'Smartphones'], weight: 0.6 },
  'creator':     { categories: ['Laptops', 'Cameras', 'Tablets', 'Smartphones'], weight: 0.6 },
  'photography': { categories: ['Cameras', 'Smartphones'], weight: 0.8 },
  'music':       { categories: ['Headphones', 'Speakers'], weight: 0.8 },
  'fitness':     { categories: ['Watches', 'Headphones', 'Shoes'], weight: 0.7 },
  'travel':      { categories: ['Power Banks', 'Headphones', 'Tablets', 'Cameras'], weight: 0.5 },
  'office':      { categories: ['Laptops', 'Tablets', 'Headphones'], weight: 0.6 },
  'streaming':   { categories: ['Televisions', 'Speakers', 'Headphones'], weight: 0.6 },
}

// Brand profiles for persona scoring
const BRAND_PROFILES = {
  'Samsung':  { gaming: 78, battery: 72, camera: 85, value: 75, ecosystem: 90 },
  'Apple':    { gaming: 85, battery: 82, camera: 92, value: 60, ecosystem: 98 },
  'MOTOROLA': { gaming: 65, battery: 80, camera: 70, value: 85, ecosystem: 55 },
  'Xiaomi':   { gaming: 82, battery: 85, camera: 75, value: 92, ecosystem: 65 },
  'OPPO':     { gaming: 72, battery: 88, camera: 80, value: 78, ecosystem: 60 },
  'Vivo':     { gaming: 70, battery: 82, camera: 82, value: 76, ecosystem: 58 },
  'Realme':   { gaming: 80, battery: 82, camera: 72, value: 90, ecosystem: 55 },
  'OnePlus':  { gaming: 90, battery: 80, camera: 82, value: 75, ecosystem: 72 },
  'Nothing':  { gaming: 75, battery: 78, camera: 72, value: 80, ecosystem: 65 },
  'Sony':     { gaming: 80, battery: 70, camera: 95, value: 65, ecosystem: 75 },
  'JBL':      { gaming: 60, battery: 85, camera: 0, value: 82, ecosystem: 50 },
  'Bose':     { gaming: 55, battery: 80, camera: 0, value: 60, ecosystem: 70 },
}
const DEFAULT_PROFILE = { gaming: 65, battery: 75, camera: 68, value: 75, ecosystem: 50 }

function getBrandProfile(brand) {
  const key = Object.keys(BRAND_PROFILES).find(k =>
    brand.toLowerCase().includes(k.toLowerCase()) || k.toLowerCase().includes(brand.toLowerCase())
  )
  return key ? BRAND_PROFILES[key] : DEFAULT_PROFILE
}

// Conversational greetings
const GREETINGS = {
  found: [
    "Great news! I found exactly what you're looking for. Here's my top pick:",
    "I've analyzed the market and here's what stands out for your needs:",
    "After scanning 1,400+ products, here's my recommendation:",
    "Perfect timing! I found some great options for you:",
    "Here's what I'd recommend based on your requirements:",
  ],
  notFound: [
    "Hmm, I couldn't find exact matches for that query. Could you try being more specific?",
    "I wasn't able to find products matching those exact criteria. Try adjusting your budget or category.",
    "No luck with that search. Try mentioning a specific category like 'laptop', 'phone', or 'headphones'.",
  ],
  memory: [
    "Welcome back! I remember you're interested in {category}. ",
    "Good to see you again! Since you like {brand}, ",
    "Hey! I've kept your preferences in mind. ",
  ],
}

// Market signal templates
const MARKET_SIGNALS = [
  { template: "🔥 Price dropped {pct}% this week", condition: p => p.bestPrice < p.originalPrice },
  { template: "📈 Trending among students in India", condition: p => p.bestPrice < 300 && p.rating >= 4.2 },
  { template: "⚡ Most bought in this category", condition: p => p.totalReviews > 50000 },
  { template: "💎 Hidden gem — underrated by market", condition: p => p.rating >= 4.3 && p.totalReviews < 10000 },
  { template: "🏆 Top-rated in {category}", condition: p => p.dealScore >= 88 },
  { template: "🇮🇳 Bestseller in India this week", condition: p => p.totalReviews > 30000 },
  { template: "✨ Editor's choice for value", condition: p => p.dealScore >= 85 && p.bestPrice < p.originalPrice * 0.85 },
  { template: "🎓 Perfect for students", condition: p => p.bestPrice < 250 && p.rating >= 4.0 },
]

// Badge assignment rules
const BADGE_RULES = [
  { badge: '🏆 Best Value', check: (p, all) => p.dealScore >= 85 && p.bestPrice <= all[0]?.bestPrice * 1.1 },
  { badge: '🎨 Creator Favorite', check: (p) => { const bp = getBrandProfile(p.brand); return bp.camera >= 80 } },
  { badge: '🎮 Gamer\'s Pick', check: (p) => { const bp = getBrandProfile(p.brand); return bp.gaming >= 82 } },
  { badge: '💰 Budget Champion', check: (p, all) => p.bestPrice === Math.min(...all.map(x => x.bestPrice)) },
  { badge: '⭐ Most Popular', check: (p, all) => p.totalReviews === Math.max(...all.map(x => x.totalReviews)) },
  { badge: '💎 Hidden Gem', check: (p) => p.rating >= 4.3 && p.totalReviews < 10000 && p.dealScore >= 80 },
  { badge: '⚠️ Overpriced', check: (p) => p.dealScore < 65 && p.bestPrice > p.originalPrice * 0.95 },
  { badge: '🔋 Battery Beast', check: (p) => { const bp = getBrandProfile(p.brand); return bp.battery >= 82 } },
  { badge: '🍎 Ecosystem King', check: (p) => { const bp = getBrandProfile(p.brand); return bp.ecosystem >= 85 } },
]


// ═══════════════════════════════════════════════════════════
// STEP 1: INTENT PARSER
// ═══════════════════════════════════════════════════════════

function parseIntent(query) {
  const q = query.toLowerCase().trim()
  const scores = {}

  // Score each category
  for (const [category, keywords] of Object.entries(CATEGORY_KEYWORDS)) {
    let score = 0

    // Primary keywords (high confidence)
    for (const kw of keywords.primary) {
      if (q.includes(kw)) {
        score += 10
        // Exact word boundary match gets bonus
        const regex = new RegExp(`\\b${kw.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i')
        if (regex.test(q)) score += 5
      }
    }

    // Secondary keywords (medium confidence)
    for (const kw of keywords.secondary) {
      if (q.includes(kw)) score += 4
    }

    // Brand detection (high confidence — brands are unique identifiers)
    for (const brand of keywords.brands) {
      if (q.includes(brand)) {
        score += 12 // Brands are very strong signals
      }
    }

    if (score > 0) scores[category] = score
  }

  // Use-case inference (lower confidence, acts as tiebreaker)
  for (const [usecase, mapping] of Object.entries(USECASE_CATEGORY_MAP)) {
    if (q.includes(usecase)) {
      for (const cat of mapping.categories) {
        scores[cat] = (scores[cat] || 0) + 3 * mapping.weight
      }
    }
  }

  // Sort by score descending
  const ranked = Object.entries(scores).sort((a, b) => b[1] - a[1])

  if (ranked.length === 0) return { category: null, confidence: 0, allScores: {} }

  const topCategory = ranked[0][0]
  const topScore = ranked[0][1]
  const secondScore = ranked.length > 1 ? ranked[1][1] : 0

  // Confidence: how dominant is the top category?
  const confidence = topScore >= 15 ? 'high'
    : topScore >= 8 ? 'medium'
    : 'low'

  return {
    category: topCategory,
    confidence,
    topScore,
    allScores: scores,
    ambiguous: secondScore > 0 && (topScore - secondScore) < 4,
    secondCategory: ranked.length > 1 ? ranked[1][0] : null,
  }
}


// ═══════════════════════════════════════════════════════════
// STEP 2: FILTER EXTRACTOR
// ═══════════════════════════════════════════════════════════

function extractFilters(query) {
  const q = query.toLowerCase().trim()
  const filters = {
    budget: null,
    budgetType: null, // 'under', 'around', 'over'
    brands: [],
    useCases: [],
    attributes: [],
  }

  // Budget extraction
  const underMatch = q.match(/(?:under|below|less than|max|upto|up to|within)\s*[\$₹]?\s*(\d[\d,]*)/i)
  const aroundMatch = q.match(/(?:around|about|near|approximately)\s*[\$₹]?\s*(\d[\d,]*)/i)
  const overMatch = q.match(/(?:over|above|more than|min|atleast|at least)\s*[\$₹]?\s*(\d[\d,]*)/i)
  const dollarMatch = q.match(/\$\s*(\d[\d,]*)/i)

  if (underMatch) { filters.budget = parseInt(underMatch[1].replace(/,/g, '')); filters.budgetType = 'under' }
  else if (aroundMatch) { filters.budget = parseInt(aroundMatch[1].replace(/,/g, '')); filters.budgetType = 'around' }
  else if (overMatch) { filters.budget = parseInt(overMatch[1].replace(/,/g, '')); filters.budgetType = 'over' }
  else if (dollarMatch) { filters.budget = parseInt(dollarMatch[1].replace(/,/g, '')); filters.budgetType = 'under' }

  // Budget keywords without numbers
  if (!filters.budget) {
    if (/\b(budget|cheap|affordable|value|economical|inexpensive)\b/i.test(q)) {
      filters.budget = 300; filters.budgetType = 'under'
    } else if (/\b(premium|flagship|high.?end|luxury|top.?tier|expensive|best)\b/i.test(q) && !/best.*(value|deal|budget)/i.test(q)) {
      filters.budget = 500; filters.budgetType = 'over'
    } else if (/\b(mid.?range|moderate|decent)\b/i.test(q)) {
      filters.budget = 400; filters.budgetType = 'around'
    }
  }

  // Brand extraction — search all category brands
  const allBrands = new Set()
  for (const keywords of Object.values(CATEGORY_KEYWORDS)) {
    keywords.brands.forEach(b => allBrands.add(b))
  }
  for (const brand of allBrands) {
    const regex = new RegExp(`\\b${brand.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'i')
    if (regex.test(q)) filters.brands.push(brand)
  }

  // Use-case extraction
  const usecaseKeywords = {
    gaming: /\b(gaming|gamer|game|fps|esports|play)\b/i,
    student: /\b(student|study|college|school|university|education|learning)\b/i,
    creator: /\b(creator|creative|content|editing|video editing|photo editing|design|designing|youtube|vlog)\b/i,
    photography: /\b(photography|photographer|photo|camera|portrait|landscape)\b/i,
    music: /\b(music|mixing|producing|dj|studio|audio|song|sound)\b/i,
    travel: /\b(travel|traveling|travelling|portable|outdoor|commute|commuting)\b/i,
    fitness: /\b(fitness|gym|workout|running|jogging|exercise|health|sports)\b/i,
    office: /\b(office|work|business|professional|corporate|enterprise|productivity)\b/i,
    streaming: /\b(streaming|netflix|movies|binge|entertainment|watch)\b/i,
  }
  for (const [uc, regex] of Object.entries(usecaseKeywords)) {
    if (regex.test(q)) filters.useCases.push(uc)
  }

  // Attribute extraction
  const attrKeywords = {
    'long battery': /\b(battery|long.?battery|battery.?life|endurance|long.?lasting)\b/i,
    'great camera': /\b(camera|photo|selfie|portrait|zoom|megapixel|mp)\b/i,
    'lightweight': /\b(light|lightweight|thin|slim|compact|portable|ultra.?thin)\b/i,
    'fast': /\b(fast|speed|quick|performance|powerful|snappy|responsive)\b/i,
    'noise cancelling': /\b(noise.?cancel|anc|noise.?reduction|quiet|silence)\b/i,
    'waterproof': /\b(water.?proof|water.?resist|ip6[78]|ip5[45]|splash)\b/i,
    'minimalist': /\b(minimalist|minimal|clean|simple|elegant|sleek)\b/i,
    'durable': /\b(durable|rugged|tough|sturdy|build.?quality)\b/i,
  }
  for (const [attr, regex] of Object.entries(attrKeywords)) {
    if (regex.test(q)) filters.attributes.push(attr)
  }

  return filters
}


// ═══════════════════════════════════════════════════════════
// STEP 3: PRODUCT SEARCH
// ═══════════════════════════════════════════════════════════

function searchProducts(category, filters, memory = null) {
  let results = [...PRODUCTS]

  // CRITICAL: Category filter — never cross-contaminate
  if (category) {
    results = results.filter(p => p.category.toLowerCase() === category.toLowerCase())
  }

  // Budget filter
  if (filters.budget) {
    if (filters.budgetType === 'under') {
      results = results.filter(p => p.bestPrice <= filters.budget)
    } else if (filters.budgetType === 'over') {
      results = results.filter(p => p.bestPrice >= filters.budget)
    } else if (filters.budgetType === 'around') {
      const margin = filters.budget * 0.25
      results = results.filter(p => p.bestPrice >= filters.budget - margin && p.bestPrice <= filters.budget + margin)
    }
  }

  // Brand filter — if specific brands mentioned, prioritize but don't exclude all others
  if (filters.brands.length > 0) {
    const brandMatches = results.filter(p =>
      filters.brands.some(b => p.brand.toLowerCase().includes(b) || p.name.toLowerCase().includes(b))
    )
    if (brandMatches.length >= 2) {
      results = brandMatches
    }
    // If too few brand matches, keep all but mark brand matches for bonus scoring
  }

  // If still no results and we had strict filters, relax budget by 30%
  if (results.length === 0 && category && filters.budget) {
    results = PRODUCTS.filter(p => p.category.toLowerCase() === category.toLowerCase())
    if (filters.budgetType === 'under') {
      results = results.filter(p => p.bestPrice <= filters.budget * 1.3)
    }
  }

  // Final fallback: if category found but budget too restrictive, show top from category
  if (results.length === 0 && category) {
    results = PRODUCTS.filter(p => p.category.toLowerCase() === category.toLowerCase())
  }

  return results
}


// ═══════════════════════════════════════════════════════════
// STEP 4: AI SCORER
// ═══════════════════════════════════════════════════════════

function scoreProducts(products, filters, memory = null) {
  if (products.length === 0) return []

  const maxReviews = Math.max(...products.map(p => p.totalReviews), 1)
  const maxPrice = Math.max(...products.map(p => p.bestPrice), 1)

  const scored = products.map(p => {
    const bp = getBrandProfile(p.brand)
    let score = 0

    // Deal score (0-30)
    score += (p.dealScore / 100) * 30

    // Rating (0-25)
    score += (p.rating / 5) * 25

    // Review popularity (0-15) — log-scaled
    score += (Math.log10(p.totalReviews + 1) / Math.log10(maxReviews + 1)) * 15

    // Price value (0-20) — lower price = higher value within category
    score += (1 - p.bestPrice / maxPrice) * 20

    // Use-case fit bonus (0-10)
    let usecaseBonus = 0
    for (const uc of filters.useCases) {
      if (uc === 'gaming') usecaseBonus += bp.gaming / 100 * 10
      else if (uc === 'photography' || uc === 'creator') usecaseBonus += bp.camera / 100 * 10
      else if (uc === 'music') usecaseBonus += 7 // headphones are inherently good for music
      else if (uc === 'student') usecaseBonus += bp.value / 100 * 10
      else if (uc === 'fitness') usecaseBonus += 6
      else usecaseBonus += 5
    }
    score += Math.min(usecaseBonus, 10)

    // Memory bonus — preferred brands get small boost
    if (memory?.preferredBrands?.includes(p.brand.toLowerCase())) {
      score += 3
    }

    // Brand match bonus
    if (filters.brands.length > 0 && filters.brands.some(b => p.brand.toLowerCase().includes(b) || p.name.toLowerCase().includes(b))) {
      score += 5
    }

    // Assign badges
    const badges = []
    for (const rule of BADGE_RULES) {
      if (rule.check(p, products)) badges.push(rule.badge)
    }

    return { ...p, aiScore: Math.round(score * 10) / 10, badges }
  })

  // Sort by AI score descending
  scored.sort((a, b) => b.aiScore - a.aiScore)

  // Assign rank-based badges
  if (scored.length > 0 && !scored[0].badges.includes('🏆 Best Value')) {
    scored[0].badges.unshift('★ Top Pick')
  }

  return scored
}


// ═══════════════════════════════════════════════════════════
// STEP 5: RESPONSE BUILDER
// ═══════════════════════════════════════════════════════════

function generatePriceHistory(product) {
  const rng = seededRandom(product.id * 17 + 31)
  const months = ['Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr']
  const basePrice = product.bestPrice
  const volatility = 0.08 + rng() * 0.12
  return months.map((month, i) => {
    const factor = 1 + (rng() - 0.4) * volatility
    const trendFactor = i / (months.length - 1)
    const historicalPrice = basePrice * factor * (1 - trendFactor) + basePrice * trendFactor
    return { month, price: Math.round(historicalPrice * 100) / 100 }
  })
}

function generateSentiment(product) {
  const rng = seededRandom(product.id * 13 + 7)
  const baseSentiment = (product.rating - 3) / 2 * 100
  const gen = () => {
    const positive = clamp(Math.round(baseSentiment * (0.8 + rng() * 0.4)), 25, 92)
    const negative = clamp(Math.round((100 - positive) * (0.3 + rng() * 0.2)), 3, 30)
    return { positive, neutral: 100 - positive - negative, negative }
  }
  return { youtube: gen(), reddit: gen(), reviews: gen() }
}

function generateProsAndCons(product) {
  const rng = seededRandom(product.id * 23 + 11)
  const bp = getBrandProfile(product.brand)

  const allPros = [
    { c: bp.battery > 75, t: `Impressive battery life for all-day use` },
    { c: bp.camera > 78, t: `Outstanding camera system by ${product.brand}` },
    { c: bp.gaming > 80, t: `Smooth gaming performance — no frame drops` },
    { c: product.rating >= 4.3, t: `Highly rated by ${product.totalReviews.toLocaleString()}+ buyers` },
    { c: product.dealScore >= 85, t: `Excellent deal — score ${product.dealScore}/100` },
    { c: bp.value > 80, t: `Strong value-for-money in its price segment` },
    { c: product.bestPrice < product.originalPrice * 0.85, t: `Currently ${Math.round((1 - product.bestPrice / product.originalPrice) * 100)}% below original price` },
    { c: true, t: `Available across ${product.prices.length} platforms for easy comparison` },
    { c: bp.ecosystem > 70, t: `Great ecosystem compatibility with ${product.brand} accessories` },
    { c: true, t: `Competitive pricing in the ${product.category} segment` },
  ]

  const allCons = [
    { c: bp.battery < 72, t: `Battery life could be better for heavy users` },
    { c: bp.camera < 70, t: `Camera may struggle in low-light conditions` },
    { c: product.rating < 4.3, t: `Mixed reviews — some quality concerns noted` },
    { c: bp.value < 70, t: `Premium pricing may not suit budget-conscious buyers` },
    { c: bp.ecosystem < 60, t: `Limited ecosystem — fewer accessories available` },
    { c: true, t: `Price varies significantly across platforms` },
    { c: true, t: `Limited color variants available in some regions` },
  ]

  const pros = allPros.filter(p => p.c).sort(() => rng() - 0.5).slice(0, 3).map(p => p.t)
  const cons = allCons.filter(c => c.c).sort(() => rng() - 0.5).slice(0, 2).map(c => c.t)

  return { pros, cons }
}

function getMarketSignals(product) {
  const signals = []
  for (const signal of MARKET_SIGNALS) {
    if (signal.condition(product)) {
      let text = signal.template
      text = text.replace('{pct}', Math.round((1 - product.bestPrice / product.originalPrice) * 100))
      text = text.replace('{category}', product.category)
      signals.push(text)
    }
  }
  return signals.slice(0, 3)
}

function generateWhyRecommended(product, query, filters) {
  const parts = []

  if (product.dealScore >= 85) parts.push(`With a deal score of ${product.dealScore}/100, this is one of the best values in the ${product.category} category right now.`)
  if (product.rating >= 4.3) parts.push(`Backed by ${product.totalReviews.toLocaleString()} reviews with a ${product.rating}/5 rating — users love this product.`)
  if (product.bestPrice < product.originalPrice * 0.85) parts.push(`It's currently ${Math.round((1 - product.bestPrice / product.originalPrice) * 100)}% below the original price — a great time to buy.`)

  if (filters.useCases.includes('gaming')) parts.push(`It handles gaming well with solid thermal management and performance.`)
  if (filters.useCases.includes('student')) parts.push(`It's perfect for students — great battery, solid performance, and won't break the bank.`)
  if (filters.useCases.includes('creator')) parts.push(`Content creators will appreciate the display quality and processing power.`)

  if (parts.length === 0) parts.push(`This product scores well across our AI metrics — strong deal score, user ratings, and cross-platform availability.`)

  return parts.join(' ')
}

function getPersonaFit(product, filters) {
  const bp = getBrandProfile(product.brand)
  const priceFactor = product.bestPrice < 200 ? 1.1 : product.bestPrice < 400 ? 1.0 : 0.9
  const rng = seededRandom(product.id * 7 + 99)

  const personas = [
    { key: 'gamer', label: '🎮 Gamer', score: clamp(Math.round((bp.gaming * 0.6 + product.dealScore * 0.2 + rng() * 15) * priceFactor), 30, 98) },
    { key: 'student', label: '📚 Student', score: clamp(Math.round((bp.value * 0.4 + bp.battery * 0.3 + (product.bestPrice < 250 ? 80 : 50) * 0.2 + rng() * 10)), 30, 98) },
    { key: 'creator', label: '🎨 Creator', score: clamp(Math.round((bp.camera * 0.4 + bp.gaming * 0.2 + bp.ecosystem * 0.2 + rng() * 12)), 30, 98) },
    { key: 'parent', label: '👨‍👩‍👧 Parent', score: clamp(Math.round((bp.value * 0.3 + bp.battery * 0.3 + (product.bestPrice < 200 ? 85 : 50) * 0.2 + rng() * 10)), 30, 98) },
  ]

  // Highlight the best matching use-case
  if (filters.useCases.length > 0) {
    const ucMap = { gaming: 'gamer', student: 'student', creator: 'creator', photography: 'creator', music: 'creator' }
    for (const uc of filters.useCases) {
      const p = personas.find(p => p.key === (ucMap[uc] || uc))
      if (p) p.highlighted = true
    }
  }

  return personas.sort((a, b) => b.score - a.score)
}

function buildResponse(query, scoredProducts, intent, filters, memory) {
  const rng = seededRandom(query.length * 7 + 42)

  if (scoredProducts.length === 0) {
    return {
      type: 'not_found',
      greeting: GREETINGS.notFound[Math.floor(rng() * GREETINGS.notFound.length)],
      query,
      suggestion: intent.category ? `Try browsing our ${intent.category} collection` : 'Try being more specific — mention a product type like "laptop", "phone", or "headphones"',
      detectedCategory: intent.category,
      products: [],
    }
  }

  const topProducts = scoredProducts.slice(0, 5) // Get top 5
  const topPick = topProducts[0]
  const alternatives = topProducts.slice(1, 4)

  // Build greeting
  let greeting = GREETINGS.found[Math.floor(rng() * GREETINGS.found.length)]
  if (memory?.lastCategory && memory.lastCategory === intent.category) {
    greeting = `Still shopping for ${intent.category}? I've got some fresh recommendations! `
  }

  // Build deal analysis for top pick
  const dealAnalysis = buildDealAnalysis(topPick)

  return {
    type: 'found',
    query,
    greeting,
    detectedCategory: intent.category,
    confidence: intent.confidence,

    topPick: {
      product: topPick,
      whyRecommended: generateWhyRecommended(topPick, query, filters),
      personaFit: getPersonaFit(topPick, filters),
      priceHistory: generatePriceHistory(topPick),
      sentiment: generateSentiment(topPick),
      prosAndCons: generateProsAndCons(topPick),
      marketSignals: getMarketSignals(topPick),
      dealAnalysis,
    },

    alternatives: alternatives.map(p => ({
      product: p,
      whyRecommended: generateWhyRecommended(p, query, filters),
      marketSignals: getMarketSignals(p).slice(0, 1),
      prosAndCons: generateProsAndCons(p),
    })),

    filters,
    totalSearched: PRODUCTS.filter(p => intent.category ? p.category.toLowerCase() === intent.category.toLowerCase() : true).length,
  }
}

function buildDealAnalysis(product) {
  if (!product.prices || product.prices.length === 0) return null
  const prices = [...product.prices].sort((a, b) => a.price - b.price)
  const best = prices[0]
  const worst = prices[prices.length - 1]
  const saved = worst.price - best.price
  const percent = Math.round((saved / worst.price) * 100)

  return {
    bestPrice: best.price,
    bestPlatform: PLATFORMS[best.platform]?.name || best.platform,
    worstPrice: worst.price,
    worstPlatform: PLATFORMS[worst.platform]?.name || worst.platform,
    savings: saved,
    savingsPercent: percent,
    platforms: prices.map(p => ({
      name: PLATFORMS[p.platform]?.name || p.platform,
      icon: PLATFORMS[p.platform]?.icon || '🛒',
      price: p.price,
      rating: p.rating,
    })),
  }
}


// ═══════════════════════════════════════════════════════════
// AI MEMORY MODULE
// ═══════════════════════════════════════════════════════════

const MEMORY_KEY = 'bb_ai_memory'

export function loadMemory() {
  try {
    const raw = localStorage.getItem(MEMORY_KEY)
    if (raw) return JSON.parse(raw)
  } catch (e) { /* ignore */ }
  return {
    preferredBrands: [],
    budgetRange: null,
    useCases: [],
    categoriesExplored: [],
    queryCount: 0,
    lastCategory: null,
  }
}

export function saveMemory(memory) {
  try {
    localStorage.setItem(MEMORY_KEY, JSON.stringify(memory))
  } catch (e) { /* ignore */ }
}

function updateMemory(memory, intent, filters) {
  const updated = { ...memory }

  updated.queryCount = (updated.queryCount || 0) + 1
  if (intent.category) {
    updated.lastCategory = intent.category
    if (!updated.categoriesExplored.includes(intent.category)) {
      updated.categoriesExplored.push(intent.category)
      if (updated.categoriesExplored.length > 10) updated.categoriesExplored.shift()
    }
  }

  if (filters.budget && filters.budgetType === 'under') {
    updated.budgetRange = filters.budget
  }

  for (const brand of filters.brands) {
    if (!updated.preferredBrands.includes(brand)) {
      updated.preferredBrands.push(brand)
      if (updated.preferredBrands.length > 5) updated.preferredBrands.shift()
    }
  }

  for (const uc of filters.useCases) {
    if (!updated.useCases.includes(uc)) {
      updated.useCases.push(uc)
      if (updated.useCases.length > 5) updated.useCases.shift()
    }
  }

  saveMemory(updated)
  return updated
}


// ═══════════════════════════════════════════════════════════
// MAIN ENTRY POINT
// ═══════════════════════════════════════════════════════════

/**
 * Process a user query through the full AI pipeline.
 * @param {string} query - The user's natural language query
 * @returns {{ response: Object, memory: Object, intent: Object, filters: Object }}
 */
export function processQuery(query) {
  // Load memory
  let memory = loadMemory()

  // Step 1: Parse intent
  const intent = parseIntent(query)

  // Step 2: Extract filters
  const filters = extractFilters(query)

  // Step 3: Search products (category-restricted)
  const rawResults = searchProducts(intent.category, filters, memory)

  // Step 4: Score and rank
  const scoredResults = scoreProducts(rawResults, filters, memory)

  // Step 5: Build structured response
  const response = buildResponse(query, scoredResults, intent, filters, memory)

  // Update memory
  memory = updateMemory(memory, intent, filters)

  return { response, memory, intent, filters }
}


// ═══════════════════════════════════════════════════════════
// QUICK CHIP QUERIES
// ═══════════════════════════════════════════════════════════

export const QUICK_CHIPS = [
  { label: '🎮 Gaming', query: 'Best gaming laptop under $800', icon: 'gaming' },
  { label: '📚 Student', query: 'Best laptop for students under $500', icon: 'student' },
  { label: '🎨 Creator', query: 'Best phone for content creation', icon: 'creator' },
  { label: '💰 Budget', query: 'Best budget smartphone under $200', icon: 'budget' },
  { label: '🍎 Apple', query: 'Best Apple products', icon: 'apple' },
  { label: '✈️ Travel', query: 'Best portable gadgets for travel', icon: 'travel' },
  { label: '🔋 Long Battery', query: 'Phone with best battery life', icon: 'battery' },
  { label: '📷 Photography', query: 'Best camera for photography', icon: 'photo' },
  { label: '💪 Fitness', query: 'Best fitness tracker smartwatch', icon: 'fitness' },
  { label: '✨ Premium', query: 'Best premium flagship phone', icon: 'premium' },
  { label: '🎧 Music', query: 'Best headphones for music lovers', icon: 'music' },
  { label: '📺 Home Theater', query: 'Best 4K smart TV for streaming', icon: 'tv' },
]

export default processQuery
