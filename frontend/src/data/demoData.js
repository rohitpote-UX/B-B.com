/* Demo data for frontend development */

export const PLATFORMS = {
  amazon: { name: 'Amazon', color: '#FF9900', icon: '🛒' },
  flipkart: { name: 'Flipkart', color: '#2874F0', icon: '🛍️' },
  myntra: { name: 'Myntra', color: '#FF3F6C', icon: '👗' },
  ajio: { name: 'Ajio', color: '#3E1F7A', icon: '🏷️' },
  croma: { name: 'Croma', color: '#00A651', icon: '💻' },
  reliance_digital: { name: 'Reliance Digital', color: '#003DAC', icon: '📱' },
  brand_store: { name: 'Brand Store', color: '#6366F1', icon: '🏬' },
}

export const PRODUCTS = [
  {
    id: 1,
    name: 'iPhone 17 Pro Max',
    brand: 'Apple',
    category: 'Smartphones',
    image: 'https://dummyjson.com/image/400x400/282828/ffffff?text=iPhone+17+Pro',
    rating: 4.7,
    totalReviews: 2847,
    bestPrice: 1149.99,
    originalPrice: 1399.99,
    bestPlatform: 'flipkart',
    dealScore: 92,
    tags: ['flagship', '5G', 'premium'],
    description: 'The most advanced iPhone ever with A19 Pro chip and 48MP quad camera.',
    specs: { Display: '6.9" OLED', Chip: 'A19 Pro', RAM: '12GB', Battery: '4852mAh', Camera: '48MP Quad' },
    features: ['A19 Pro Chip', '48MP Camera', 'Titanium Design', 'USB-C', 'ProMotion 120Hz'],
    prices: [
      { platform: 'amazon', price: 1199.99, original: 1399.99, delivery: 2, rating: 4.5 },
      { platform: 'flipkart', price: 1149.99, original: 1399.99, delivery: 1, rating: 4.6 },
      { platform: 'croma', price: 1249.99, original: 1399.99, delivery: 3, rating: 4.3 },
      { platform: 'reliance_digital', price: 1189.99, original: 1399.99, delivery: 2, rating: 4.4 },
      { platform: 'brand_store', price: 1299.99, original: 1399.99, delivery: 5, rating: 4.8 },
    ],
  },
  {
    id: 2,
    name: 'Samsung Galaxy S26 Ultra',
    brand: 'Samsung',
    category: 'Smartphones',
    image: 'https://dummyjson.com/image/400x400/1a1a2e/ffffff?text=Galaxy+S26',
    rating: 4.6,
    totalReviews: 3125,
    bestPrice: 1099.99,
    originalPrice: 1349.99,
    bestPlatform: 'amazon',
    dealScore: 88,
    tags: ['flagship', 'AI', 'S Pen'],
    description: 'Galaxy AI powered experience with 200MP camera and Snapdragon 8 Gen 5.',
    specs: { Display: '6.8" AMOLED', Chip: 'SD 8 Gen 5', RAM: '16GB', Battery: '5500mAh', Camera: '200MP' },
    features: ['Galaxy AI', '200MP Camera', 'S Pen', 'Snapdragon 8 Gen 5', 'IP68'],
    prices: [
      { platform: 'amazon', price: 1099.99, original: 1349.99, delivery: 1, rating: 4.5 },
      { platform: 'flipkart', price: 1129.99, original: 1349.99, delivery: 2, rating: 4.4 },
      { platform: 'croma', price: 1199.99, original: 1349.99, delivery: 3, rating: 4.2 },
      { platform: 'reliance_digital', price: 1149.99, original: 1349.99, delivery: 2, rating: 4.3 },
    ],
  },
  {
    id: 3,
    name: 'MacBook Pro 16" M5 Pro',
    brand: 'Apple',
    category: 'Laptops',
    image: 'https://dummyjson.com/image/400x400/2d2d2d/ffffff?text=MacBook+Pro',
    rating: 4.8,
    totalReviews: 1543,
    bestPrice: 2199.99,
    originalPrice: 2599.99,
    bestPlatform: 'amazon',
    dealScore: 85,
    tags: ['pro', 'M5', 'creator'],
    description: 'Supercharged by M5 Pro chip with 22-hour battery and Liquid Retina XDR.',
    specs: { Display: '16.2" XDR', Chip: 'M5 Pro', RAM: '36GB', Storage: '512GB SSD', Battery: '22hrs' },
    features: ['M5 Pro Chip', 'Liquid Retina XDR', '22hr Battery', 'Thunderbolt 5'],
    prices: [
      { platform: 'amazon', price: 2199.99, original: 2599.99, delivery: 2, rating: 4.7 },
      { platform: 'flipkart', price: 2249.99, original: 2599.99, delivery: 3, rating: 4.5 },
      { platform: 'croma', price: 2299.99, original: 2599.99, delivery: 4, rating: 4.3 },
      { platform: 'brand_store', price: 2399.99, original: 2599.99, delivery: 5, rating: 4.9 },
    ],
  },
  {
    id: 4,
    name: 'Dell XPS 15 (2026)',
    brand: 'Dell',
    category: 'Laptops',
    image: 'https://dummyjson.com/image/400x400/1e3a5f/ffffff?text=Dell+XPS+15',
    rating: 4.5,
    totalReviews: 892,
    bestPrice: 1599.99,
    originalPrice: 1899.99,
    bestPlatform: 'flipkart',
    dealScore: 79,
    tags: ['ultrabook', 'OLED', 'RTX'],
    description: 'Infinity Edge OLED display with Intel Ultra 9 and RTX 4070.',
    specs: { Display: '15.6" 3.5K OLED', Chip: 'Ultra 9', RAM: '32GB', GPU: 'RTX 4070', Weight: '1.86kg' },
    features: ['3.5K OLED', 'Intel Ultra 9', 'RTX 4070', 'Thunderbolt 4'],
    prices: [
      { platform: 'amazon', price: 1649.99, original: 1899.99, delivery: 2, rating: 4.4 },
      { platform: 'flipkart', price: 1599.99, original: 1899.99, delivery: 1, rating: 4.5 },
      { platform: 'croma', price: 1699.99, original: 1899.99, delivery: 3, rating: 4.2 },
    ],
  },
  {
    id: 5,
    name: 'Nike Air Max 270 React',
    brand: 'Nike',
    category: 'Shoes',
    image: 'https://dummyjson.com/image/400x400/111111/ffffff?text=Nike+Air+Max',
    rating: 4.4,
    totalReviews: 5621,
    bestPrice: 129.99,
    originalPrice: 179.99,
    bestPlatform: 'myntra',
    dealScore: 90,
    tags: ['running', 'lifestyle', 'comfort'],
    description: 'Iconic Air Max cushioning meets React foam for all-day comfort.',
    specs: { Type: 'Running/Lifestyle', Sole: 'Air Max + React', Upper: 'Mesh', Weight: '310g' },
    features: ['Air Max Cushioning', 'React Foam', 'Breathable Mesh', 'Rubber Outsole'],
    prices: [
      { platform: 'amazon', price: 149.99, original: 179.99, delivery: 3, rating: 4.3 },
      { platform: 'flipkart', price: 139.99, original: 179.99, delivery: 2, rating: 4.4 },
      { platform: 'myntra', price: 129.99, original: 179.99, delivery: 4, rating: 4.5 },
      { platform: 'ajio', price: 134.99, original: 179.99, delivery: 5, rating: 4.2 },
      { platform: 'brand_store', price: 159.99, original: 179.99, delivery: 3, rating: 4.7 },
    ],
  },
  {
    id: 6,
    name: 'Adidas Ultraboost 24',
    brand: 'Adidas',
    category: 'Shoes',
    image: 'https://dummyjson.com/image/400x400/1a1a1a/ffffff?text=Ultraboost+24',
    rating: 4.5,
    totalReviews: 4832,
    bestPrice: 139.99,
    originalPrice: 199.99,
    bestPlatform: 'ajio',
    dealScore: 87,
    tags: ['running', 'BOOST', 'sustainable'],
    description: 'Legendary comfort with Light BOOST midsole and Primeknit+ upper.',
    specs: { Type: 'Running', Sole: 'BOOST + LEP', Upper: 'Primeknit+', Weight: '298g' },
    features: ['Light BOOST Midsole', 'Primeknit+', 'Continental Rubber', 'Recycled Materials'],
    prices: [
      { platform: 'amazon', price: 159.99, original: 199.99, delivery: 2, rating: 4.4 },
      { platform: 'flipkart', price: 149.99, original: 199.99, delivery: 3, rating: 4.3 },
      { platform: 'myntra', price: 144.99, original: 199.99, delivery: 4, rating: 4.5 },
      { platform: 'ajio', price: 139.99, original: 199.99, delivery: 5, rating: 4.6 },
    ],
  },
  {
    id: 7,
    name: 'Sony WH-1000XM6',
    brand: 'Sony',
    category: 'Headphones',
    image: 'https://dummyjson.com/image/400x400/2a2a2a/ffffff?text=Sony+XM6',
    rating: 4.7,
    totalReviews: 3456,
    bestPrice: 329.99,
    originalPrice: 429.99,
    bestPlatform: 'amazon',
    dealScore: 94,
    tags: ['ANC', 'wireless', 'Hi-Res'],
    description: 'Industry-leading noise cancellation with 40-hour battery and Hi-Res audio.',
    specs: { Type: 'Over-ear', ANC: 'HD V3', Battery: '40hrs', Driver: '40mm', Weight: '250g' },
    features: ['Industry-leading ANC', '40hr Battery', 'Hi-Res Audio', 'Multipoint', 'DSEE Extreme'],
    prices: [
      { platform: 'amazon', price: 329.99, original: 429.99, delivery: 1, rating: 4.6 },
      { platform: 'flipkart', price: 339.99, original: 429.99, delivery: 2, rating: 4.5 },
      { platform: 'croma', price: 349.99, original: 429.99, delivery: 3, rating: 4.3 },
    ],
  },
  {
    id: 8,
    name: 'Bose QC Ultra Headphones',
    brand: 'Bose',
    category: 'Headphones',
    image: 'https://dummyjson.com/image/400x400/3d3d3d/ffffff?text=Bose+QC+Ultra',
    rating: 4.6,
    totalReviews: 2134,
    bestPrice: 349.99,
    originalPrice: 429.99,
    bestPlatform: 'flipkart',
    dealScore: 82,
    tags: ['ANC', 'immersive', 'comfort'],
    description: 'Immersive audio with Bose Immersive Audio and world-class ANC.',
    specs: { Type: 'Over-ear', ANC: 'Quiet Mode', Battery: '24hrs', Driver: '35mm', Weight: '250g' },
    features: ['Bose Immersive Audio', 'CustomTune EQ', 'World-class ANC', 'Plush Cushions'],
    prices: [
      { platform: 'amazon', price: 359.99, original: 429.99, delivery: 2, rating: 4.5 },
      { platform: 'flipkart', price: 349.99, original: 429.99, delivery: 1, rating: 4.6 },
      { platform: 'croma', price: 379.99, original: 429.99, delivery: 4, rating: 4.2 },
    ],
  },
  {
    id: 9,
    name: 'Dyson V15 Detect Vacuum',
    brand: 'Dyson',
    category: 'Home Appliance',
    image: 'https://dummyjson.com/image/400x400/5a5a5a/ffffff?text=Dyson+V15',
    rating: 4.8,
    totalReviews: 4120,
    bestPrice: 649.99,
    originalPrice: 749.99,
    bestPlatform: 'amazon',
    dealScore: 89,
    tags: ['vacuum', 'smart home', 'cleaning'],
    description: 'The most powerful, intelligent cordless vacuum with laser illumination.',
    specs: { Type: 'Cordless', Suction: '240 AW', Battery: '60 mins', Weight: '3.1kg' },
    features: ['Laser Illumination', 'Piezo Sensor', 'LCD Screen', 'Anti-tangle'],
    prices: [
      { platform: 'amazon', price: 649.99, original: 749.99, delivery: 2, rating: 4.8 },
      { platform: 'croma', price: 699.99, original: 749.99, delivery: 3, rating: 4.6 },
      { platform: 'reliance_digital', price: 679.99, original: 749.99, delivery: 2, rating: 4.7 }
    ],
  },
  {
    id: 10,
    name: 'Levi\'s 501 Original Fit',
    brand: 'Levi\'s',
    category: 'mens wear',
    image: 'https://dummyjson.com/image/400x400/123456/ffffff?text=Levis+501',
    rating: 4.5,
    totalReviews: 12450,
    bestPrice: 59.99,
    originalPrice: 89.99,
    bestPlatform: 'myntra',
    dealScore: 95,
    tags: ['denim', 'classic', 'fashion'],
    description: 'The blueprint for all denim. The 501 Original is a cultural icon.',
    specs: { Fit: 'Straight', Rise: 'Mid', Material: '100% Cotton Base', Closure: 'Button Fly' },
    features: ['Classic Straight Leg', 'Five-pocket styling', 'Signature Levi\'s tab', 'Durable Denim'],
    prices: [
      { platform: 'myntra', price: 59.99, original: 89.99, delivery: 3, rating: 4.5 },
      { platform: 'amazon', price: 69.99, original: 89.99, delivery: 2, rating: 4.4 },
      { platform: 'ajio', price: 64.99, original: 89.99, delivery: 4, rating: 4.3 }
    ],
  },
  {
    id: 11,
    name: 'Zara Silk Blend Wrap Dress',
    brand: 'Zara',
    category: 'ladies wear',
    image: 'https://dummyjson.com/image/400x400/9e3d4a/ffffff?text=Zara+Dress',
    rating: 4.6,
    totalReviews: 830,
    bestPrice: 89.99,
    originalPrice: 129.99,
    bestPlatform: 'ajio',
    dealScore: 91,
    tags: ['dress', 'silk', 'evening'],
    description: 'Elegant midi wrap dress constructed with a premium silk blend.',
    specs: { Fabric: '70% Silk, 30% Viscose', Length: 'Midi', Care: 'Dry Clean Only', Fit: 'Wrap Flowy' },
    features: ['V-neckline', 'Tie waist', 'Flowing silhouette', 'Premium feel'],
    prices: [
      { platform: 'ajio', price: 89.99, original: 129.99, delivery: 4, rating: 4.6 },
      { platform: 'myntra', price: 99.99, original: 129.99, delivery: 3, rating: 4.5 },
      { platform: 'brand_store', price: 129.99, original: 129.99, delivery: 5, rating: 4.8 }
    ],
  },
  {
    id: 12,
    name: 'Oshkosh B\'gosh Denim Overalls',
    brand: 'Oshkosh',
    category: 'kids Wear',
    image: 'https://dummyjson.com/image/400x400/4a7db8/ffffff?text=Kids+Overalls',
    rating: 4.9,
    totalReviews: 3210,
    bestPrice: 24.99,
    originalPrice: 38.00,
    bestPlatform: 'amazon',
    dealScore: 88,
    tags: ['kids', 'clothing', 'durable'],
    description: 'Classic durable denim overalls made for active kids.',
    specs: { Material: '100% Cotton', Age: '2T - 5T', Care: 'Machine Wash', Type: 'Overalls' },
    features: ['Adjustable straps', 'Genuine metal hardware', 'Vestbak trick', 'Multiple pockets'],
    prices: [
      { platform: 'amazon', price: 24.99, original: 38.00, delivery: 2, rating: 4.9 },
      { platform: 'flipkart', price: 29.99, original: 38.00, delivery: 3, rating: 4.7 }
    ],
  },
  {
    id: 13,
    name: 'Ray-Ban Classic Aviator',
    brand: 'Ray-Ban',
    category: 'fashion and accessories',
    image: 'https://dummyjson.com/image/400x400/202020/ffffff?text=Ray-Ban+Aviator',
    rating: 4.7,
    totalReviews: 18500,
    bestPrice: 154.00,
    originalPrice: 180.00,
    bestPlatform: 'brand_store',
    dealScore: 82,
    tags: ['sunglasses', 'classic', 'accessories'],
    description: 'Currently one of the most iconic sunglass models in the world.',
    specs: { Frame: 'Metalized Gold', Lens: 'G-15 Green', Polarization: 'Standard', Fit: 'Standard' },
    features: ['100% UV Protection', 'Adjustable nose pads', 'Classic teardrop lens', 'Durable frame'],
    prices: [
      { platform: 'amazon', price: 160.00, original: 180.00, delivery: 1, rating: 4.5 },
      { platform: 'brand_store', price: 154.00, original: 180.00, delivery: 4, rating: 4.9 },
      { platform: 'myntra', price: 165.00, original: 180.00, delivery: 3, rating: 4.6 }
    ],
  },
  {
    id: 14,
    name: 'Brooks Brothers Dress Shirt',
    brand: 'Brooks Brothers',
    category: 'office wear',
    image: 'https://dummyjson.com/image/400x400/ffffff/000000?text=Brooks+Brothers',
    rating: 4.6,
    totalReviews: 1250,
    bestPrice: 85.00,
    originalPrice: 120.00,
    bestPlatform: 'amazon',
    dealScore: 86,
    tags: ['work', 'formal', 'shirt'],
    description: 'Brooks Brothers Non-Iron Traditional Fit Dress Shirt. Professional precision.',
    specs: { Fit: 'Traditional', Material: 'Oxford Cloth', Care: 'Non-iron', Collar: 'Button-down' },
    features: ['Wrinkle resistant', 'Supima cotton', 'Puckering-free seams', 'Classic fit'],
    prices: [
      { platform: 'amazon', price: 85.00, original: 120.00, delivery: 2, rating: 4.6 },
      { platform: 'brand_store', price: 120.00, original: 120.00, delivery: 5, rating: 4.9 }
    ],
  },
  {
    id: 15,
    name: 'Colgate Total Advanced Pack',
    brand: 'Colgate',
    category: 'everyday essential',
    image: 'https://dummyjson.com/image/400x400/e31837/ffffff?text=Colgate+Total',
    rating: 4.8,
    totalReviews: 32410,
    bestPrice: 12.99,
    originalPrice: 16.99,
    bestPlatform: 'amazon',
    dealScore: 98,
    tags: ['health', 'daily', 'hygiene'],
    description: 'Premium everyday essential providing 12-hour antibacterial protection.',
    specs: { Size: '4x 5.1oz', Type: 'Whitening Paste', Flavor: 'Mint', Use: 'Daily' },
    features: ['Cavity Protection', 'Enamel Strengthening', 'Breath Freshening', 'Stain Removal'],
    prices: [
      { platform: 'amazon', price: 12.99, original: 16.99, delivery: 1, rating: 4.8 },
      { platform: 'flipkart', price: 14.99, original: 16.99, delivery: 1, rating: 4.7 }
    ],
  },
  {
    id: 16,
    name: 'Rolex Submariner Date',
    brand: 'Rolex',
    category: 'premium Products',
    image: 'https://dummyjson.com/image/400x400/01553d/ffffff?text=Rolex+Submariner',
    rating: 4.9,
    totalReviews: 342,
    bestPrice: 10250.00,
    originalPrice: 10250.00,
    bestPlatform: 'brand_store',
    dealScore: 75,
    tags: ['luxury', 'watch', 'investment'],
    description: 'The supreme reference among divers’ watches. An absolute cultural icon of luxury.',
    specs: { Material: 'Oystersteel', Bezel: 'Cerachrom', Reserve: '70 hours', WaterResistance: '300m' },
    features: ['Perpetual mechanical movement', 'Cyclops lens', 'Chromalight display', 'Unidirectional bezel'],
    prices: [
      { platform: 'brand_store', price: 10250.00, original: 10250.00, delivery: 14, rating: 5.0 },
      { platform: 'amazon', price: 11500.00, original: 10250.00, delivery: 3, rating: 4.8 }
    ],
  },
  {
    id: 17,
    name: 'LG C3 65" OLED 4K TV',
    brand: 'LG',
    category: 'electronics',
    image: 'https://dummyjson.com/image/400x400/222222/ffffff?text=LG+OLED+C3',
    rating: 4.8,
    totalReviews: 2950,
    bestPrice: 1499.99,
    originalPrice: 2099.99,
    bestPlatform: 'amazon',
    dealScore: 93,
    tags: ['tv', 'oled', '4k'],
    description: 'Unparalleled pure black colors and infinite contrast powered by the a9 AI Processor Gen6.',
    specs: { Panel: 'OLED evo', Resolution: '4K', Refresh_Rate: '120Hz', Processor: 'a9 Gen 6' },
    features: ['Dolby Vision', 'WebOS 23', 'NVIDIA G-Sync', 'Brightness Booster'],
    prices: [
      { platform: 'amazon', price: 1499.99, original: 2099.99, delivery: 2, rating: 4.7 },
      { platform: 'croma', price: 1649.99, original: 2099.99, delivery: 4, rating: 4.8 },
      { platform: 'reliance_digital', price: 1599.99, original: 2099.99, delivery: 3, rating: 4.6 }
    ],
  }
]

// Procedurally pad all categories to contain exactly 10 distinct products
const existingCategories = [...new Set(PRODUCTS.map(p => p.category))]
existingCategories.forEach(category => {
  const existing = PRODUCTS.filter(p => p.category === category)
  const toAdd = 10 - existing.length
  
  if (toAdd > 0) {
    const template = existing[0]
    const prefixes = ['Pro', 'Ultra', 'Elite', 'Essential', 'Plus', 'V2', 'Advanced', 'Max', 'Edition', 'Signature']
    
    for (let i = 0; i < toAdd; i++) {
        PRODUCTS.push({
          ...template,
          id: PRODUCTS.length + 1000,
          name: `${template.name.split(' ')[0]} ${prefixes[i] || `Variant ${i}`} Series`,
          bestPrice: Math.round((template.bestPrice * (0.6 + Math.random() * 0.8)) * 100) / 100,
          dealScore: Math.floor(70 + Math.random() * 28),
          rating: Math.round((4.0 + Math.random() * 1.0) * 10) / 10,
          totalReviews: Math.floor(Math.random() * 5000),
          image: template.image.replace('text=', `text=Type+${i+1}+`)
        })
    }
  }
})

export const TRENDING_COMPARISONS = [
  { id: 1, products: [PRODUCTS[0], PRODUCTS[1]], title: 'iPhone 17 Pro Max vs Galaxy S26 Ultra', views: 45200, category: 'Smartphones' },
  { id: 2, products: [PRODUCTS[4], PRODUCTS[5]], title: 'Nike Air Max vs Adidas Ultraboost', views: 32100, category: 'Shoes' },
  { id: 3, products: [PRODUCTS[6], PRODUCTS[7]], title: 'Sony XM6 vs Bose QC Ultra', views: 28400, category: 'Headphones' },
  { id: 4, products: [PRODUCTS[2], PRODUCTS[3]], title: 'MacBook Pro M5 vs Dell XPS 15', views: 21800, category: 'Laptops' },
]

export const DEALS = PRODUCTS.map((p, i) => ({
  id: i + 1,
  product: p,
  platform: p.bestPlatform,
  discount: Math.round(((p.originalPrice - p.bestPrice) / p.originalPrice) * 100),
  dealScore: p.dealScore,
  expiresIn: Math.floor(Math.random() * 72) + 12, // hours
})).sort((a, b) => b.dealScore - a.dealScore)

export const TESTIMONIALS = [
  { name: 'Priya Sharma', role: 'Tech Enthusiast', avatar: '👩‍💻', quote: 'Brand Battle saved me ₹15,000 on my laptop! The price comparison across platforms is incredible.', rating: 5 },
  { name: 'Rahul Mehra', role: 'Smart Shopper', avatar: '🧑‍💼', quote: 'The AI advisor recommended the perfect phone for my budget. Absolutely game-changing!', rating: 5 },
  { name: 'Anita Desai', role: 'Fashion Buyer', avatar: '👗', quote: 'I never buy shoes without checking Brand Battle first. The deal quality scores are spot on.', rating: 5 },
  { name: 'Vikram Singh', role: 'Gadget Reviewer', avatar: '📱', quote: 'As a tech reviewer, I use Brand Battle for every comparison. The AI summaries are remarkably accurate.', rating: 5 },
]

export const HOW_IT_WORKS = [
  { step: 1, title: 'Search Any Product', description: 'Type what you\'re looking for — we search across all major platforms instantly.', icon: '🔍', color: 'var(--color-accent)' },
  { step: 2, title: 'Compare & Analyze', description: 'See side-by-side comparisons with AI-powered insights and winner indicators.', icon: '⚔️', color: 'var(--color-cyan)' },
  { step: 3, title: 'Find Best Deal', description: 'Our AI scans all platforms to find the absolute best price and genuine deals.', icon: '💰', color: 'var(--color-emerald)' },
  { step: 4, title: 'Buy with Confidence', description: 'Make your purchase knowing you got the best product at the best price.', icon: '🏆', color: 'var(--color-amber)' },
]

export const generatePriceHistory = (basePrice, days = 90) => {
  const data = []
  const now = new Date()
  for (let i = days; i >= 0; i--) {
    const date = new Date(now)
    date.setDate(date.getDate() - i)
    const variation = 0.85 + Math.random() * 0.3
    data.push({
      date: date.toISOString().split('T')[0],
      amazon: Math.round(basePrice * (0.9 + Math.random() * 0.2) * 100) / 100,
      flipkart: Math.round(basePrice * (0.88 + Math.random() * 0.22) * 100) / 100,
      lowest: Math.round(basePrice * variation * 100) / 100,
    })
  }
  return data
}
