// Product type matching demoData.js structure
export interface ProductPrice {
  platform: string;
  price: number;
  original: number;
  delivery: number;
  rating: number;
}

export interface Product {
  id: number;
  name: string;
  brand: string;
  category: string;
  image: string;
  rating: number;
  totalReviews: number;
  bestPrice: number;
  originalPrice: number;
  bestPlatform: string;
  dealScore: number;
  tags: string[];
  description: string;
  specs: Record<string, string | number | undefined>;
  features: string[];
  prices: ProductPrice[];
  productUrl?: string;
  flipkartUrl?: string;
  feedBadge?: string;
}

export interface Platform {
  name: string;
  color: string;
  icon: string;
}

export interface PlatformMap {
  [key: string]: Platform;
}

export interface Deal {
  id: number;
  product: Product;
  platform: string;
  discount: number;
  dealScore: number;
}

export interface PriceAlert {
  id: number;
  productId: number;
  productName: string;
  productBrand: string;
  productImage: string;
  bestPrice: number;
  targetPrice: number;
  platforms: string[];
  email: string;
  createdAt: string;
}

export interface PriceHistoryPoint {
  date: string;
  amazon: number;
  flipkart: number;
}

export interface AIMessage {
  role: 'user' | 'assistant';
  content?: string;
  data?: AIResponse;
}

export interface AIResponse {
  type: string;
  title: string;
  subtitle?: string;
  products?: Product[];
  summary?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

export interface AIMemory {
  queryCount: number;
  lastCategory: string | null;
  preferredBrands: string[];
  budgetRange: { min: number; max: number } | null;
  previousQueries: string[];
}
