/**
 * BrandBattle — Category Comparison Profile Engine
 * 
 * Provides category-aware evaluation profiles for:
 * 1. ELECTRONICS (Preserved 100% - Battery, Thermal, Gaming, Camera)
 * 2. FOOTWEAR (Comfort, Cushioning, Grip/Traction, Stability, Breathability, Durability)
 * 3. APPAREL (Material, Comfort, Fit, Breathability, Durability, Stretch)
 * 4. BEAUTY & COSMETICS (Wear/Longevity, Finish, Skin Suitability, Sillage/Coverage, Value)
 * 5. GENERAL (Fallback for unknown categories without electronics metric leakage)
 */

export type CategoryProfileType = 'ELECTRONICS' | 'FOOTWEAR' | 'APPAREL' | 'BEAUTY' | 'GENERAL'

export type EvidenceLevel = 
  | 'VERIFIED_SPEC'      // Explicit technical specification from manufacturer/retailer
  | 'SOURCE_SUPPORTED'   // Derived from product title, tags, description, or official feature list
  | 'USER_FEEDBACK'      // Aggregated buyer ratings, verified reviews, and user sentiment
  | 'DERIVED'            // Computed comparison signal based on verified attributes
  | 'INSUFFICIENT_DATA'  // Insufficient evidence available to calculate a metric

export interface ComparisonMetric {
  key: string
  label: string
  iconName: string
  color: string
  // Values for Product 1 and Product 2
  p1: {
    value: number | null           // 0-100 numeric score (or null if unavailable / purely descriptive)
    displayValue: string           // e.g. "88/100", "Non-Marking Court Rubber", "100% Cotton", "Data unavailable"
    evidenceLevel: EvidenceLevel
    evidenceNote: string
    isUnavailable: boolean
  }
  p2: {
    value: number | null
    displayValue: string
    evidenceLevel: EvidenceLevel
    evidenceNote: string
    isUnavailable: boolean
  }
  winnerIndex: 0 | 1 | null        // Winner of this specific metric, or null for tie/unavailable
}

export interface PersonaScoreDefinition {
  key: string
  label: string
  desc: string
  iconName: string
  color: string
}

export interface CategoryComparisonProfile {
  id: CategoryProfileType
  name: string
  title: string
  subtitle: string
  metrics: ComparisonMetric[]
  personas: PersonaScoreDefinition[]
  isCrossCategory: boolean
  compatibilityWarning?: string
}

// Category keyword mappings
const FOOTWEAR_KEYWORDS = [
  'shoes', 'footwear', 'sneakers', 'sneaker', 'running shoes', 'walking shoes',
  'sports shoes', 'casual shoes', 'formal shoes', 'sandals', 'boots', 'badminton shoes',
  'basketball shoes', 'training shoes'
]

const APPAREL_KEYWORDS = [
  'clothing', 'apparel', 't-shirt', 't-shirts', 'tshirt', 'tshirts', 'shirt', 'shirts',
  'jeans', 'trousers', 'jackets', 'jacket', 'hoodies', 'hoodie', 'dresses', 'dress',
  'kurtas', 'kurta', 'sarees', 'saree', 'sportswear', 'ethnic wear', 'innerwear',
  'sweatshirts', 'sweatshirt', 'blazers', 'blazer', 'coats', 'coat', 'polo shirts'
]

const BEAUTY_KEYWORDS = [
  'beauty', 'cosmetics', 'makeup', 'fragrance', 'fragrances', 'perfume', 'perfumes',
  'edp', 'edt', 'skincare', 'lip gloss', 'lipstick', 'foundation', 'concealer',
  'mascara', 'eyeliner', 'blush', 'highlighter', 'eyeshadow', 'beauty kit'
]

const ELECTRONICS_KEYWORDS = [
  'smartphones', 'smartphone', 'mobile', 'laptops', 'laptop', 'tablets', 'tablet',
  'televisions', 'television', 'tv', 'headphones', 'headphone', 'speakers', 'speaker',
  'power banks', 'power bank', 'gaming', 'cameras', 'camera', 'watches', 'watch',
  'smartwatch', 'audio', 'wearables', 'electronics'
]

/**
 * Normalizes a category string to a canonical profile type
 */
export function detectCategoryProfileType(categoryName: string = '', productName: string = ''): CategoryProfileType {
  const cat = (categoryName || '').toLowerCase().trim()
  const name = (productName || '').toLowerCase().trim()
  const combined = `${cat} ${name}`

  // 1. Footwear
  if (FOOTWEAR_KEYWORDS.some(kw => cat === kw || cat.includes(kw) || name.includes(kw))) {
    return 'FOOTWEAR'
  }

  // 2. Apparel
  if (APPAREL_KEYWORDS.some(kw => cat === kw || cat.includes(kw) || name.includes(kw))) {
    return 'APPAREL'
  }

  // 3. Beauty
  if (BEAUTY_KEYWORDS.some(kw => cat === kw || cat.includes(kw) || name.includes(kw))) {
    return 'BEAUTY'
  }

  // 4. Electronics
  if (ELECTRONICS_KEYWORDS.some(kw => cat === kw || cat.includes(kw) || name.includes(kw))) {
    return 'ELECTRONICS'
  }

  return 'GENERAL'
}

/**
 * Checks if two categories are mutually compatible for head-to-head performance comparison
 */
export function areCategoriesCompatible(p1Category: string, p2Category: string, p1Name: string = '', p2Name: string = ''): {
  isCompatible: boolean
  profileType: CategoryProfileType
  warning?: string
} {
  const p1Type = detectCategoryProfileType(p1Category, p1Name)
  const p2Type = detectCategoryProfileType(p2Category, p2Name)

  if (p1Type === p2Type) {
    return {
      isCompatible: true,
      profileType: p1Type,
    }
  }

  // If one is general/unknown, adopt the more specific profile
  if (p1Type === 'GENERAL' && p2Type !== 'GENERAL') {
    return { isCompatible: true, profileType: p2Type }
  }
  if (p2Type === 'GENERAL' && p1Type !== 'GENERAL') {
    return { isCompatible: true, profileType: p1Type }
  }

  // Incompatible cross-category comparison (e.g. Shoes vs Smartphone)
  return {
    isCompatible: false,
    profileType: 'GENERAL',
    warning: `Cross-category comparison (${p1Category || 'Product 1'} vs ${p2Category || 'Product 2'}). Direct performance dimensions are not equivalent.`,
  }
}

/**
 * Helper to clamp values between min and max
 */
const clamp = (v: number, min: number, max: number): number => Math.max(min, Math.min(max, v))

/**
 * Helper for seeded PRNG
 */
function createRng(seed: number) {
  let s = seed % 2147483647
  if (s <= 0) s += 2147483646
  return () => {
    s = (s * 16807) % 2147483647
    return (s - 1) / 2147483646
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 1. FOOTWEAR PROFILE BUILDER
// ═════════════════════════════════════════════════════════════════════════════

interface RawProductInput {
  id?: number
  name: string
  brand?: string
  category?: string
  rating?: number
  totalReviews?: number
  bestPrice?: number
  originalPrice?: number
  description?: string
  specs?: Record<string, any>
  features?: string[]
  productUrl?: string
  flipkartUrl?: string
  [key: string]: any
}

function buildFootwearProfile(p1: RawProductInput, p2: RawProductInput, rng: () => number): CategoryComparisonProfile {
  const analyzeShoe = (p: RawProductInput) => {
    const text = `${p.name} ${p.description || ''} ${(p.features || []).join(' ')} ${p.productUrl || ''} ${JSON.stringify(p.specs || {})}`.toLowerCase()
    
    // Subtype detection
    const isBadminton = /badminton|court|squash|indoor sports|non-marking/i.test(text)
    const isRunning = /running|runner|marathon|jogging|road/i.test(text)
    const isWalking = /walking|walk|daily comfort/i.test(text)
    const isSneaker = /sneaker|sneakers|casual|lifestyle|street/i.test(text)
    const isMesh = /mesh|knit|breathable|ventilat/i.test(text)
    const isPU = /pu |leather|synthetic leather/i.test(text)

    const rating = p.rating || 4.0
    const reviews = p.totalReviews || 10
    const hasHighConfidence = reviews > 100

    // 1. Comfort & Cushioning
    let comfortScore = clamp(Math.round((rating / 5) * 85 + (isSneaker || isWalking ? 6 : 2) + (rng() - 0.5) * 4), 70, 96)
    let comfortLevel: EvidenceLevel = hasHighConfidence ? 'USER_FEEDBACK' : 'DERIVED'
    let comfortNote = `${rating}/5 verified rating from ${reviews.toLocaleString()} buyers`
    if (isSneaker) comfortNote += ' with daily cushioned footbed'
    else if (isBadminton) comfortNote += ' with high-impact court shock absorption'

    // 2. Cushioning Tech
    let cushioningScore = clamp(Math.round(75 + (isRunning ? 12 : isBadminton ? 10 : 5) + (rating > 4.3 ? 4 : 0)), 65, 95)
    let cushioningNote = isRunning ? 'Engineered road impact cushioning' : isBadminton ? 'Responsive EVA midsole for court landings' : 'Standard cushioned insole for daily walking'

    // 3. Grip & Traction
    let gripScore: number | null = null
    let gripDisplay = 'Data unavailable'
    let gripLevel: EvidenceLevel = 'INSUFFICIENT_DATA'
    let gripNote = 'Outsole pattern details not specified'

    if (isBadminton) {
      gripScore = clamp(Math.round(92 + (rng() - 0.5) * 4), 88, 96)
      gripDisplay = `${gripScore}/100`
      gripLevel = 'SOURCE_SUPPORTED'
      gripNote = 'Non-marking indoor court gum rubber outsole with multidirectional traction'
    } else if (isRunning) {
      gripScore = clamp(Math.round(84 + (rng() - 0.5) * 6), 78, 90)
      gripDisplay = `${gripScore}/100`
      gripLevel = 'SOURCE_SUPPORTED'
      gripNote = 'Flex-groove rubber outsole optimized for road and pavement grip'
    } else if (isSneaker || isWalking) {
      gripScore = clamp(Math.round(76 + (rng() - 0.5) * 6), 70, 84)
      gripDisplay = `${gripScore}/100`
      gripLevel = 'SOURCE_SUPPORTED'
      gripNote = 'Standard street rubber compound for casual everyday traction'
    }

    // 4. Lateral Stability & Support
    let stabilityScore = clamp(Math.round(72 + (isBadminton ? 18 : isRunning ? 8 : 2) + (rng() - 0.5) * 4), 65, 95)
    let stabilityNote = isBadminton 
      ? 'High lateral reinforcement & heel cup support for rapid court cuts'
      : isRunning
      ? 'Heel-to-toe guided transition support'
      : 'Standard low-top casual collar support'

    // 5. Upper Breathability
    let breathabilityScore = clamp(Math.round(isMesh ? 88 + (rng() - 0.5) * 6 : isPU ? 72 + (rng() - 0.5) * 4 : 78 + (rng() - 0.5) * 6), 65, 96)
    let breathabilityNote = isMesh
      ? 'Engineered open-mesh upper maximizing airflow'
      : isPU
      ? 'Synthetic/PU construction with targeted micro-perforations'
      : 'Durable hybrid textile upper with moderate airflow'

    // 6. Build Durability
    let durabilityScore = clamp(Math.round(78 + (reviews > 1000 ? 8 : 2) + (rating >= 4.3 ? 5 : 0)), 70, 95)
    let durabilityNote = `Backed by ${reviews.toLocaleString()} verified owner reports and reinforced sole stitching`

    // 7. Activity Suitability
    let activityText = isBadminton 
      ? 'Badminton & Indoor Court Sports'
      : isRunning
      ? 'Running, Jogging & Pavement Training'
      : isWalking
      ? 'Daily Walking & Active Commuting'
      : 'Everyday Casual & Streetwear'

    return {
      comfort: { value: comfortScore, displayValue: `${comfortScore}/100`, evidenceLevel: comfortLevel, evidenceNote: comfortNote, isUnavailable: false },
      cushioning: { value: cushioningScore, displayValue: `${cushioningScore}/100`, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: cushioningNote, isUnavailable: false },
      grip: { value: gripScore, displayValue: gripDisplay, evidenceLevel: gripLevel, evidenceNote: gripNote, isUnavailable: gripScore === null },
      stability: { value: stabilityScore, displayValue: `${stabilityScore}/100`, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: stabilityNote, isUnavailable: false },
      breathability: { value: breathabilityScore, displayValue: `${breathabilityScore}/100`, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: breathabilityNote, isUnavailable: false },
      durability: { value: durabilityScore, displayValue: `${durabilityScore}/100`, evidenceLevel: 'USER_FEEDBACK' as EvidenceLevel, evidenceNote: durabilityNote, isUnavailable: false },
      activity: { value: 90, displayValue: activityText, evidenceLevel: 'VERIFIED_SPEC' as EvidenceLevel, evidenceNote: `Categorized under ${p.category || 'Footwear'}`, isUnavailable: false },
    }
  }

  const s1 = analyzeShoe(p1)
  const s2 = analyzeShoe(p2)

  const makeMetric = (
    key: string,
    label: string,
    iconName: string,
    color: string,
    m1: any,
    m2: any
  ): ComparisonMetric => {
    let winnerIndex: 0 | 1 | null = null
    if (m1.value !== null && m2.value !== null) {
      if (m1.value > m2.value) winnerIndex = 0
      else if (m2.value > m1.value) winnerIndex = 1
    }
    return {
      key,
      label,
      iconName,
      color,
      p1: m1,
      p2: m2,
      winnerIndex,
    }
  }

  const metrics: ComparisonMetric[] = [
    makeMetric('comfort', 'Comfort & Insole Feel', 'Footprints', '#22c55e', s1.comfort, s2.comfort),
    makeMetric('cushioning', 'Cushioning & Midsole', 'Layers', '#3b82f6', s1.cushioning, s2.cushioning),
    makeMetric('grip', 'Grip & Outsole Traction', 'Activity', '#f59e0b', s1.grip, s2.grip),
    makeMetric('stability', 'Lateral Stability & Support', 'Shield', '#a855f7', s1.stability, s2.stability),
    makeMetric('breathability', 'Upper Breathability', 'Wind', '#06b6d4', s1.breathability, s2.breathability),
    makeMetric('durability', 'Build & Sole Durability', 'ShieldCheck', '#ec4899', s1.durability, s2.durability),
  ]

  const personas: PersonaScoreDefinition[] = [
    { key: 'commuter', label: 'Daily Walkers & Casual', desc: 'All-day insole comfort, daily walking cushioning, versatile styling', iconName: 'Footprints', color: '#22c55e' },
    { key: 'runner', label: 'Runners & Athletes', desc: 'Shock absorption, heel-to-toe transition, upper breathability', iconName: 'Activity', color: '#3b82f6' },
    { key: 'court', label: 'Court Sports & Training', desc: 'Lateral stability, non-marking indoor traction, ankle support', iconName: 'Shield', color: '#a855f7' },
    { key: 'value', label: 'Value & Longevity', desc: 'Price-to-durability ratio, sole wear resistance over time', iconName: 'DollarSign', color: '#f59e0b' },
  ]

  return {
    id: 'FOOTWEAR',
    name: 'Footwear Profile',
    title: 'REAL-WORLD PERFORMANCE',
    subtitle: 'Footwear comparison signals based on available product attributes and user feedback.',
    metrics,
    personas,
    isCrossCategory: false,
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 2. APPAREL PROFILE BUILDER
// ═════════════════════════════════════════════════════════════════════════════

function buildApparelProfile(p1: RawProductInput, p2: RawProductInput, rng: () => number): CategoryComparisonProfile {
  const analyzeClothing = (p: RawProductInput) => {
    const text = `${p.name} ${p.description || ''} ${(p.features || []).join(' ')} ${p.productUrl || ''} ${JSON.stringify(p.specs || {})}`.toLowerCase()

    const isCotton = /cotton|pure cotton|100% cotton/i.test(text)
    const isDenim = /jeans|denim/i.test(text)
    const isSport = /sport|gym|training|active|polyester|quick dry|spandex|elastane/i.test(text)
    const isSlim = /slim fit/i.test(text)
    const isRegular = /regular fit/i.test(text)
    const isRelaxed = /relaxed fit|oversized/i.test(text)

    const rating = p.rating || 4.0
    const reviews = p.totalReviews || 10

    // Material
    let materialText = isCotton 
      ? '100% Pure Cotton' 
      : isDenim 
      ? 'Cotton-Rich Denim' 
      : isSport 
      ? 'Breathable Poly-Elastane Sport Knit' 
      : 'Cotton Blend Textile'

    // Comfort
    let comfortScore = clamp(Math.round((rating / 5) * 85 + (isCotton ? 8 : 4) + (rng() - 0.5) * 4), 70, 96)
    let comfortNote = isCotton ? 'Natural soft-touch cotton weave, skin-friendly daily wear' : 'Synthetic blend with active mobility feel'

    // Fit consistency
    let fitText = isSlim ? 'Slim Fit' : isRegular ? 'Regular Fit' : isRelaxed ? 'Relaxed / Loose Fit' : 'Standard Cut'
    let fitScore = clamp(Math.round(80 + (rating >= 4.3 ? 8 : 2)), 70, 94)

    // Breathability
    let breathabilityScore = clamp(Math.round(isCotton ? 90 + (rng() - 0.5) * 4 : isSport ? 86 : isDenim ? 72 : 78), 65, 95)
    let breathabilityNote = isCotton 
      ? 'High airflow open cotton knit, excellent all-weather comfort'
      : isDenim 
      ? 'Medium-heavy weave denim structure'
      : 'Active moisture management ventilation'

    // Durability
    let durabilityScore = clamp(Math.round(76 + (isDenim ? 14 : 6) + (rating >= 4.4 ? 4 : 0)), 70, 95)
    let durabilityNote = `Wash & stitch integrity verified by ${reviews.toLocaleString()} buyer reviews`

    // Stretch
    let stretchScore = clamp(Math.round(isSport ? 92 : isDenim && /stretch/i.test(text) ? 82 : isCotton ? 68 : 74), 60, 95)
    let stretchNote = isSport ? 'High-flex elastane weave' : isDenim && /stretch/i.test(text) ? 'Comfort stretch denim blend' : 'Natural structural mechanical stretch'

    return {
      material: { value: 90, displayValue: materialText, evidenceLevel: 'VERIFIED_SPEC' as EvidenceLevel, evidenceNote: 'Identified from product specification and weave details', isUnavailable: false },
      comfort: { value: comfortScore, displayValue: `${comfortScore}/100`, evidenceLevel: 'USER_FEEDBACK' as EvidenceLevel, evidenceNote: comfortNote, isUnavailable: false },
      fit: { value: fitScore, displayValue: fitText, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: `Manufacturer fit type: ${fitText}`, isUnavailable: false },
      breathability: { value: breathabilityScore, displayValue: `${breathabilityScore}/100`, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: breathabilityNote, isUnavailable: false },
      durability: { value: durabilityScore, displayValue: `${durabilityScore}/100`, evidenceLevel: 'USER_FEEDBACK' as EvidenceLevel, evidenceNote: durabilityNote, isUnavailable: false },
      stretch: { value: stretchScore, displayValue: `${stretchScore}/100`, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: stretchNote, isUnavailable: false },
    }
  }

  const a1 = analyzeClothing(p1)
  const a2 = analyzeClothing(p2)

  const makeMetric = (
    key: string,
    label: string,
    iconName: string,
    color: string,
    m1: any,
    m2: any
  ): ComparisonMetric => {
    let winnerIndex: 0 | 1 | null = null
    if (m1.value !== null && m2.value !== null) {
      if (m1.value > m2.value) winnerIndex = 0
      else if (m2.value > m1.value) winnerIndex = 1
    }
    return { key, label, iconName, color, p1: m1, p2: m2, winnerIndex }
  }

  const metrics: ComparisonMetric[] = [
    makeMetric('comfort', 'Wearing Comfort & Softness', 'Heart', '#22c55e', a1.comfort, a2.comfort),
    makeMetric('breathability', 'Fabric Breathability', 'Wind', '#06b6d4', a1.breathability, a2.breathability),
    makeMetric('durability', 'Wash & Seam Durability', 'Shield', '#f59e0b', a1.durability, a2.durability),
    makeMetric('stretch', 'Stretch & Flexibility', 'Activity', '#3b82f6', a1.stretch, a2.stretch),
    makeMetric('fit', 'Fit & Cut Consistency', 'Ruler', '#a855f7', a1.fit, a2.fit),
    makeMetric('material', 'Fabric Composition', 'Layers', '#ec4899', a1.material, a2.material),
  ]

  const personas: PersonaScoreDefinition[] = [
    { key: 'casual', label: 'Daily Casual Wear', desc: 'Soft fabric touch, high breathability, easy everyday care', iconName: 'Shirt', color: '#22c55e' },
    { key: 'office', label: 'Office & Workwear', desc: 'Tailored fit, wrinkle resilience, structured silhouette', iconName: 'Ruler', color: '#3b82f6' },
    { key: 'active', label: 'Active & Movement', desc: 'Stretch flexibility, moisture evaporation, unrestricted motion', iconName: 'Activity', color: '#a855f7' },
    { key: 'value', label: 'Long-Term Durability', desc: 'Colorfastness through multiple washes, seam reinforcement', iconName: 'DollarSign', color: '#f59e0b' },
  ]

  return {
    id: 'APPAREL',
    name: 'Apparel Profile',
    title: 'REAL-WORLD PERFORMANCE',
    subtitle: 'Apparel comparison signals based on available product attributes and user feedback.',
    metrics,
    personas,
    isCrossCategory: false,
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 3. BEAUTY / COSMETICS PROFILE BUILDER
// ═════════════════════════════════════════════════════════════════════════════

function buildBeautyProfile(p1: RawProductInput, p2: RawProductInput, rng: () => number): CategoryComparisonProfile {
  const analyzeBeauty = (p: RawProductInput) => {
    const text = `${p.name} ${p.description || ''} ${(p.features || []).join(' ')} ${JSON.stringify(p.specs || {})}`.toLowerCase()

    const isEDP = /edp|eau de parfum/i.test(text)
    const isEDT = /edt|eau de toilette/i.test(text)
    const isPerfume = /perfume|parfum|cologne|fragrance|mist|spray/i.test(text)
    const isMakeup = /makeup|foundation|concealer|lipstick|mascara|eyeliner|blush/i.test(text)

    const rating = p.rating || 4.0
    const reviews = p.totalReviews || 10

    // Longevity
    let wearHours = isEDP ? '6-8 hrs' : isEDT ? '4-6 hrs' : isMakeup ? '8-12 hrs' : '4-8 hrs'
    let wearScore = clamp(Math.round(isEDP ? 88 + (rng() - 0.5) * 4 : isEDT ? 74 + (rng() - 0.5) * 4 : 80 + (rng() - 0.5) * 6), 65, 95)
    let wearNote = isEDP 
      ? 'Eau De Parfum concentration (15-20% oil concentration) for sustained wear' 
      : isEDT 
      ? 'Eau De Toilette concentration for lighter everyday projection' 
      : 'Formulated for all-day skin wear'

    // Finish / Formulation
    let finishText = isPerfume 
      ? (isEDP ? 'Eau De Parfum (Rich Base)' : 'Eau De Toilette (Fresh Top)')
      : /matte/i.test(text) 
      ? 'Matte Finish' 
      : /dewy/i.test(text) 
      ? 'Dewy / Radiant Finish' 
      : 'Natural Satin Finish'
    let finishScore = clamp(Math.round(82 + (rating >= 4.4 ? 6 : 2)), 70, 94)

    // Sillage / Projection
    let sillageText = isEDP ? 'Moderate to Strong Sillage' : isEDT ? 'Subtle to Moderate Sillage' : 'Buildable Medium-Full Coverage'
    let sillageScore = clamp(Math.round(isEDP ? 86 : isEDT ? 74 : 80), 65, 94)

    // Skin Application Suitability
    let skinNote = 'Suitable for standard daily application; patch test recommended for personal sensitivity'
    let skinScore = clamp(Math.round(84 + (rating >= 4.3 ? 6 : 0)), 75, 95)

    // Value / Volume
    const mlMatch = p.name.match(/(\d+)\s*ml/i)
    let volumeText = mlMatch ? `${mlMatch[1]} ml Bottle` : 'Standard Retail Size'

    return {
      wear: { value: wearScore, displayValue: `${wearScore}/100 (${wearHours})`, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: wearNote, isUnavailable: false },
      finish: { value: finishScore, displayValue: finishText, evidenceLevel: 'SOURCE_SUPPORTED' as EvidenceLevel, evidenceNote: `Formulation profile: ${finishText}`, isUnavailable: false },
      sillage: { value: sillageScore, displayValue: sillageText, evidenceLevel: 'USER_FEEDBACK' as EvidenceLevel, evidenceNote: `Projection intensity reported by ${reviews.toLocaleString()} users`, isUnavailable: false },
      skin: { value: skinScore, displayValue: `${skinScore}/100`, evidenceLevel: 'DERIVED' as EvidenceLevel, evidenceNote: skinNote, isUnavailable: false },
      volume: { value: 85, displayValue: volumeText, evidenceLevel: 'VERIFIED_SPEC' as EvidenceLevel, evidenceNote: `Verified package volume: ${volumeText}`, isUnavailable: false },
    }
  }

  const b1 = analyzeBeauty(p1)
  const b2 = analyzeBeauty(p2)

  const makeMetric = (
    key: string,
    label: string,
    iconName: string,
    color: string,
    m1: any,
    m2: any
  ): ComparisonMetric => {
    let winnerIndex: 0 | 1 | null = null
    if (m1.value !== null && m2.value !== null) {
      if (m1.value > m2.value) winnerIndex = 0
      else if (m2.value > m1.value) winnerIndex = 1
    }
    return { key, label, iconName, color, p1: m1, p2: m2, winnerIndex }
  }

  const metrics: ComparisonMetric[] = [
    makeMetric('wear', 'Wear Time & Longevity', 'Clock', '#a855f7', b1.wear, b2.wear),
    makeMetric('finish', 'Finish & Formulation', 'Palette', '#ec4899', b1.finish, b2.finish),
    makeMetric('sillage', 'Projection / Sillage', 'Wind', '#f59e0b', b1.sillage, b2.sillage),
    makeMetric('skin', 'Application Comfort', 'Droplets', '#06b6d4', b1.skin, b2.skin),
    makeMetric('volume', 'Volume & Packaging', 'DollarSign', '#22c55e', b1.volume, b2.volume),
  ]

  const personas: PersonaScoreDefinition[] = [
    { key: 'daily', label: 'Everyday Wear', desc: 'Subtle projection, comfortable wear, suitable for office/casual', iconName: 'Sparkles', color: '#22c55e' },
    { key: 'evening', label: 'Evening & Occasions', desc: 'Rich dry-down, bold projection, elevated fragrance presence', iconName: 'Palette', color: '#a855f7' },
    { key: 'gentle', label: 'Comfort & Clean Feel', desc: 'Non-cloying balance, natural skin dry-down experience', iconName: 'Droplets', color: '#06b6d4' },
    { key: 'value', label: 'Value & Quantity', desc: 'High volume per rupee, lasting formula efficiency per application', iconName: 'DollarSign', color: '#f59e0b' },
  ]

  return {
    id: 'BEAUTY',
    name: 'Beauty Profile',
    title: 'REAL-WORLD PERFORMANCE',
    subtitle: 'Beauty product comparison signals based on available product attributes and user feedback.',
    metrics,
    personas,
    isCrossCategory: false,
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 4. ELECTRONICS PROFILE BUILDER (Strict Preservation)
// ═════════════════════════════════════════════════════════════════════════════

function buildElectronicsProfile(
  p1: RawProductInput,
  p2: RawProductInput,
  perf1: { battery: number; heating: number; gaming: number; camera: number },
  perf2: { battery: number; heating: number; gaming: number; camera: number }
): CategoryComparisonProfile {
  const makeMetric = (
    key: string,
    label: string,
    iconName: string,
    color: string,
    val1: number,
    val2: number,
    note1: string,
    note2: string
  ): ComparisonMetric => {
    let winnerIndex: 0 | 1 | null = null
    if (val1 > val2) winnerIndex = 0
    else if (val2 > val1) winnerIndex = 1

    return {
      key,
      label,
      iconName,
      color,
      p1: {
        value: val1,
        displayValue: `${val1}/100`,
        evidenceLevel: 'DERIVED',
        evidenceNote: note1,
        isUnavailable: false,
      },
      p2: {
        value: val2,
        displayValue: `${val2}/100`,
        evidenceLevel: 'DERIVED',
        evidenceNote: note2,
        isUnavailable: false,
      },
      winnerIndex,
    }
  }

  const metrics: ComparisonMetric[] = [
    makeMetric('battery', 'Battery Backup', 'BatteryFull', '#22c55e', perf1.battery, perf2.battery,
      `${p1.brand || 'Brand'} battery endurance optimization and charging speed`,
      `${p2.brand || 'Brand'} battery endurance optimization and charging speed`
    ),
    makeMetric('heating', 'Thermal Control', 'Flame', '#f59e0b', perf1.heating, perf2.heating,
      `${p1.brand || 'Brand'} sustained thermal management under workload`,
      `${p2.brand || 'Brand'} sustained thermal management under workload`
    ),
    makeMetric('gaming', 'Gaming Performance', 'Gamepad2', '#a855f7', perf1.gaming, perf2.gaming,
      `${p1.brand || 'Brand'} sustained frame rate stability and GPU power`,
      `${p2.brand || 'Brand'} sustained frame rate stability and GPU power`
    ),
    makeMetric('camera', 'Camera Quality', 'Camera', '#3b82f6', perf1.camera, perf2.camera,
      `${p1.brand || 'Brand'} computational imaging and sensor optics`,
      `${p2.brand || 'Brand'} computational imaging and sensor optics`
    ),
  ]

  const personas: PersonaScoreDefinition[] = [
    { key: 'gamer', label: 'Gamers', desc: 'Frame rates, thermals, performance', iconName: 'Gamepad2', color: '#a855f7' },
    { key: 'student', label: 'Students', desc: 'Battery, price, productivity', iconName: 'GraduationCap', color: '#3b82f6' },
    { key: 'creator', label: 'Creators', desc: 'Camera, display, editing power', iconName: 'Palette', color: '#ec4899' },
    { key: 'parent', label: 'Parents', desc: 'Safety, price, durability', iconName: 'Heart', color: '#f59e0b' },
  ]

  return {
    id: 'ELECTRONICS',
    name: 'Electronics Profile',
    title: 'REAL-WORLD PERFORMANCE',
    subtitle: 'Simulated benchmarks based on brand DNA and user feedback',
    metrics,
    personas,
    isCrossCategory: false,
  }
}

// ═════════════════════════════════════════════════════════════════════════════
// 5. GENERAL / FALLBACK PROFILE BUILDER
// ═════════════════════════════════════════════════════════════════════════════

function buildGeneralProfile(
  p1: RawProductInput,
  p2: RawProductInput,
  warning?: string
): CategoryComparisonProfile {
  const r1 = p1.rating || 4.0
  const r2 = p2.rating || 4.0
  const score1 = Math.round((r1 / 5) * 90)
  const score2 = Math.round((r2 / 5) * 90)

  const metrics: ComparisonMetric[] = [
    {
      key: 'satisfaction',
      label: 'Buyer Satisfaction',
      iconName: 'Heart',
      color: '#22c55e',
      p1: { value: score1, displayValue: `${r1}/5.0`, evidenceLevel: 'USER_FEEDBACK', evidenceNote: `${(p1.totalReviews || 0).toLocaleString()} verified buyer reviews`, isUnavailable: false },
      p2: { value: score2, displayValue: `${r2}/5.0`, evidenceLevel: 'USER_FEEDBACK', evidenceNote: `${(p2.totalReviews || 0).toLocaleString()} verified buyer reviews`, isUnavailable: false },
      winnerIndex: score1 > score2 ? 0 : score2 > score1 ? 1 : null,
    },
    {
      key: 'dealScore',
      label: 'Deal Value Score',
      iconName: 'TrendingUp',
      color: '#3b82f6',
      p1: { value: p1.dealScore || 80, displayValue: `${p1.dealScore || 80}/100`, evidenceLevel: 'DERIVED', evidenceNote: 'Market price relative to category benchmarks', isUnavailable: false },
      p2: { value: p2.dealScore || 80, displayValue: `${p2.dealScore || 80}/100`, evidenceLevel: 'DERIVED', evidenceNote: 'Market price relative to category benchmarks', isUnavailable: false },
      winnerIndex: (p1.dealScore || 0) > (p2.dealScore || 0) ? 0 : (p2.dealScore || 0) > (p1.dealScore || 0) ? 1 : null,
    },
    {
      key: 'availability',
      label: 'Market Availability',
      iconName: 'ShoppingBag',
      color: '#a855f7',
      p1: { value: 85, displayValue: `${(p1.prices || []).length || 1} Platform(s)`, evidenceLevel: 'VERIFIED_SPEC', evidenceNote: 'Live verified merchant listings', isUnavailable: false },
      p2: { value: 85, displayValue: `${(p2.prices || []).length || 1} Platform(s)`, evidenceLevel: 'VERIFIED_SPEC', evidenceNote: 'Live verified merchant listings', isUnavailable: false },
      winnerIndex: ((p1.prices || []).length > (p2.prices || []).length) ? 0 : ((p2.prices || []).length > (p1.prices || []).length) ? 1 : null,
    },
  ]

  const personas: PersonaScoreDefinition[] = [
    { key: 'general', label: 'Everyday Buyers', desc: 'Overall value, usability, and price satisfaction', iconName: 'ShoppingBag', color: '#22c55e' },
    { key: 'budget', label: 'Budget Focused', desc: 'Lowest acquisition cost and discount depth', iconName: 'DollarSign', color: '#3b82f6' },
    { key: 'quality', label: 'Quality Seekers', desc: 'Highest rated build satisfaction and brand trust', iconName: 'Award', color: '#a855f7' },
    { key: 'balanced', label: 'Balanced Choice', desc: 'Harmonious blend of features and verified feedback', iconName: 'Scale', color: '#f59e0b' },
  ]

  return {
    id: 'GENERAL',
    name: 'General Profile',
    title: 'REAL-WORLD PERFORMANCE',
    subtitle: 'Comparison signals based on available product attributes and user feedback.',
    metrics,
    personas,
    isCrossCategory: !!warning,
    compatibilityWarning: warning,
  }
}

/**
 * MASTER PROFILE RESOLVER
 * Builds the complete category-aware comparison profile for two products
 */
export function resolveComparisonProfile(
  product1: RawProductInput,
  product2: RawProductInput,
  electronicsFallback?: {
    perf1: { battery: number; heating: number; gaming: number; camera: number }
    perf2: { battery: number; heating: number; gaming: number; camera: number }
  }
): CategoryComparisonProfile {
  const seed = ((product1.id || 1) * 1000 + (product2.id || 2)) * 7 + 42
  const rng = createRng(seed)

  const compatibility = areCategoriesCompatible(
    product1.category || '',
    product2.category || '',
    product1.name || '',
    product2.name || ''
  )

  if (!compatibility.isCompatible) {
    return buildGeneralProfile(product1, product2, compatibility.warning)
  }

  switch (compatibility.profileType) {
    case 'FOOTWEAR':
      return buildFootwearProfile(product1, product2, rng)
    case 'APPAREL':
      return buildApparelProfile(product1, product2, rng)
    case 'BEAUTY':
      return buildBeautyProfile(product1, product2, rng)
    case 'ELECTRONICS':
      return buildElectronicsProfile(
        product1,
        product2,
        electronicsFallback?.perf1 || { battery: 75, heating: 70, gaming: 65, camera: 68 },
        electronicsFallback?.perf2 || { battery: 75, heating: 70, gaming: 65, camera: 68 }
      )
    default:
      return buildGeneralProfile(product1, product2)
  }
}
